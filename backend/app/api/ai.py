import logging
from pathlib import PurePosixPath
from typing import Annotated
from uuid import UUID, uuid4

from botocore.exceptions import BotoCoreError
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from kombu.exceptions import KombuError
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.auth import CurrentUser
from app.core.config import get_settings
from app.core.storage import get_s3_client, put_object
from app.db.models import AIJob, KnowledgeDocument, User
from app.db.session import get_db_session
from app.worker import celery_app

logger = logging.getLogger("school_erp.ai")
router = APIRouter(prefix="/ai", tags=["AI assistant"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
MAX_DOCUMENT_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".md"}


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)

    @field_validator("question")
    @classmethod
    def trim_question(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("The question must contain at least three non-whitespace characters")
        return value


class JobResponse(BaseModel):
    id: UUID
    status: str


class KnowledgeDocumentResponse(JobResponse):
    filename: str


def require_ai_role(user: User) -> None:
    if user.role not in {"school_admin", "teacher"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature is only available to school administrators and teachers",
        )


@router.post("/documents", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_knowledge_document(
    user: CurrentUser,
    db: DbSession,
    document: Annotated[UploadFile, File()],
) -> JobResponse:
    require_ai_role(user)
    filename = PurePosixPath((document.filename or "").replace("\\", "/")).name
    extension = PurePosixPath(filename).suffix.casefold()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only plain-text .txt and Markdown .md documents are supported",
        )

    content = await document.read(MAX_DOCUMENT_BYTES + 1)
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document is empty")
    if len(content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Document size must not exceed 5 MiB",
        )
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The document must be UTF-8 encoded",
        ) from exc

    document_id = uuid4()
    object_key = f"schools/{user.school_id}/knowledge/{document_id}/{filename}"
    try:
        await run_in_threadpool(put_object, object_key, content, "text/plain; charset=utf-8")
        record = KnowledgeDocument(
            id=document_id,
            school_id=user.school_id,
            uploaded_by=user.id,
            filename=filename,
            object_key=object_key,
        )
        db.add(record)
        await db.commit()
    except (BotoCoreError, SQLAlchemyError):
        await db.rollback()
        logger.exception("Unable to store uploaded knowledge document")
        try:
            settings = get_settings()
            await run_in_threadpool(
                get_s3_client().delete_object,
                Bucket=settings.s3_bucket,
                Key=object_key,
            )
        except BotoCoreError:
            logger.exception("Unable to clean up uploaded object after failed database write")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save the document; please retry",
        ) from None

    try:
        celery_app.send_task(
            "app.tasks.index_knowledge_document",
            args=[str(document_id)],
            task_id=str(document_id),
        )
    except KombuError:
        logger.exception("Unable to enqueue document indexing task")
        record.status = "failed"
        record.error_message = "Document indexing could not be queued"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document saved but indexing is temporarily unavailable",
        ) from None
    return JobResponse(id=document_id, status="queued")


@router.get("/documents", response_model=list[KnowledgeDocumentResponse])
async def list_knowledge_documents(
    user: CurrentUser,
    db: DbSession,
) -> list[KnowledgeDocumentResponse]:
    require_ai_role(user)
    documents = await db.scalars(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.school_id == user.school_id)
        .order_by(KnowledgeDocument.created_at.desc())
    )
    return [
        KnowledgeDocumentResponse(
            id=document.id,
            status=document.status,
            filename=document.filename,
        )
        for document in documents
    ]


@router.post("/ask", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def ask_school_assistant(
    payload: AskRequest,
    user: CurrentUser,
    db: DbSession,
) -> JobResponse:
    require_ai_role(user)
    job_id = uuid4()
    db.add(
        AIJob(
            id=job_id,
            school_id=user.school_id,
            user_id=user.id,
            question=payload.question.strip(),
        )
    )
    await db.commit()
    try:
        celery_app.send_task(
            "app.tasks.answer_school_question",
            args=[str(job_id)],
            task_id=str(job_id),
        )
    except KombuError:
        logger.exception("Unable to enqueue AI question")
        job = await db.get(AIJob, job_id)
        if job is not None:
            job.status = "failed"
            await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI worker is unavailable; please retry",
        ) from None
    return JobResponse(id=job_id, status="queued")


@router.get("/jobs/{job_id}")
async def get_ai_job(job_id: UUID, user: CurrentUser, db: DbSession) -> dict[str, object]:
    job = await db.scalar(
        select(AIJob).where(
            AIJob.id == job_id,
            AIJob.school_id == user.school_id,
            AIJob.user_id == user.id,
        )
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI job not found")

    response: dict[str, object] = {"id": job.id, "status": job.status}
    if job.answer is not None:
        response["answer"] = job.answer
        response["provider"] = job.provider or get_settings().ai_provider
    if job.error_message is not None:
        response["error"] = job.error_message
    return response
