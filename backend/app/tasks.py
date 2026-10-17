import asyncio
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ai.agent import ask_school_agent
from app.ai.ingestion import index_school_document
from app.core.config import get_settings
from app.core.storage import get_object
from app.db.models import AIJob, KnowledgeDocument
from app.worker import celery_app

logger = logging.getLogger("school_erp.tasks")


async def _set_document_status(document_id: UUID, status: str, error: str | None = None) -> None:
    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            document = await session.get(KnowledgeDocument, document_id)
            if document is not None:
                document.status = status
                document.error_message = error
                await session.commit()
    finally:
        await engine.dispose()


async def _index_document(document_id: UUID) -> None:
    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            document = await session.get(KnowledgeDocument, document_id)
            if document is None:
                raise ValueError("Knowledge document does not exist")
            document.status = "processing"
            await session.commit()
            school_id = document.school_id
            object_key = document.object_key
            filename = document.filename
        content = await asyncio.to_thread(get_object, object_key)
        chunks = await asyncio.to_thread(index_school_document, school_id, filename, content)
        await _set_document_status(document_id, "ready")
        logger.info(
            "Indexed school document",
            extra={"document_id": str(document_id), "chunks": chunks},
        )
    except Exception as exc:
        logger.exception("School document indexing failed", extra={"document_id": str(document_id)})
        await _set_document_status(document_id, "failed", "Document indexing failed")
        raise exc
    finally:
        await engine.dispose()


@celery_app.task(name="app.tasks.index_knowledge_document")
def index_knowledge_document(document_id: str) -> None:
    asyncio.run(_index_document(UUID(document_id)))


async def _answer_question(job_id: UUID) -> dict[str, str]:
    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            job = await session.scalar(select(AIJob).where(AIJob.id == job_id))
            if job is None:
                raise ValueError("AI job does not exist")
            job.status = "processing"
            await session.commit()
            school_id, question = job.school_id, job.question

        answer = await asyncio.to_thread(ask_school_agent, school_id, question)
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            job = await session.get(AIJob, job_id)
            if job is not None:
                job.status = "completed"
                job.answer = answer["answer"]
                job.provider = answer["provider"]
                await session.commit()
        return answer
    except Exception:
        logger.exception("AI question task failed", extra={"job_id": str(job_id)})
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            job = await session.get(AIJob, job_id)
            if job is not None:
                job.status = "failed"
                job.error_message = "The AI task could not be completed"
                await session.commit()
        raise
    finally:
        await engine.dispose()


@celery_app.task(name="app.tasks.answer_school_question")
def answer_school_question(job_id: str) -> dict[str, str]:
    return asyncio.run(_answer_question(UUID(job_id)))
