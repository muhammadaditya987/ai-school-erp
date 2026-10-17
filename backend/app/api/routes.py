from fastapi import APIRouter, HTTPException
from kombu import Connection
from kombu.exceptions import KombuError
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.core.config import get_settings
from app.core.redis_client import redis_client
from app.db.session import engine

router = APIRouter()
router.include_router(auth_router)
router.include_router(ai_router)
settings = get_settings()


@router.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", tags=["health"])
async def readiness() -> dict[str, str]:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        await redis_client.ping()
        await run_in_threadpool(_check_rabbitmq)
    except (SQLAlchemyError, RedisError, KombuError) as exc:
        raise HTTPException(status_code=503, detail="A required service is unavailable") from exc
    return {"status": "ready"}


def _check_rabbitmq() -> None:
    with Connection(settings.rabbitmq_url, connect_timeout=2) as connection:
        connection.ensure_connection(max_retries=0)
