from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.schemas import AccessTokenResponse, SchoolRegistration, UserResponse
from app.core.config import get_settings
from app.db.models import School, User, UserRole
from app.db.session import get_db_session

router = APIRouter(prefix="/auth", tags=["authentication"])
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
settings = get_settings()

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def _create_access_token(user_id: UUID) -> str:
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": expires_at,
            "iss": settings.app_name,
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authenticate_access_token(token: str, db: AsyncSession) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=["HS256"],
            issuer=settings.app_name,
        )
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise _unauthorized()
        user_id = UUID(subject)
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise _unauthorized() from exc

    user = await db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise _unauthorized()
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    return await authenticate_access_token(token, db)


CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_school(payload: SchoolRegistration, db: DbSession) -> User:
    normalized_email = str(payload.email).lower()
    existing = await db.scalar(
        select(User.id).where(User.email == normalized_email)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    school_exists = await db.scalar(select(School.id).where(School.slug == payload.school_slug))
    if school_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="School URL is already taken",
        )

    hashed_password = await run_in_threadpool(password_hash.hash, payload.password)
    school = School(name=payload.school_name.strip(), slug=payload.school_slug)
    try:
        db.add(school)
        await db.flush()
        user = User(
            school_id=school.id,
            email=normalized_email,
            full_name=payload.full_name.strip(),
            hashed_password=hashed_password,
            role=UserRole.SCHOOL_ADMIN,
        )
        db.add(user)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or school URL is already registered",
        ) from exc

    await db.refresh(user)
    return user


@router.post("/token", response_model=AccessTokenResponse)
async def create_access_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> AccessTokenResponse:
    user = await db.scalar(select(User).where(User.email == form.username.lower()))
    if user is None or not await run_in_threadpool(
        password_hash.verify,
        form.password,
        user.hashed_password,
    ):
        raise _unauthorized()

    return AccessTokenResponse(
        access_token=_create_access_token(user.id),
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def read_current_user(user: CurrentUser) -> User:
    return user
