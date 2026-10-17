from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db_session
from app.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db_session, None)
        await engine.dispose()


def registration_payload() -> dict[str, str]:
    return {
        "school_name": "North School",
        "school_slug": "north-school",
        "full_name": "School Admin",
        "email": "admin@northschool.example.com",
        "password": "correct-horse-battery-staple",
    }


@pytest.mark.asyncio
async def test_school_registration_and_oauth_login_create_tenant_scoped_user(
    client: AsyncClient,
) -> None:
    registration = await client.post("/api/v1/auth/register", json=registration_payload())

    assert registration.status_code == 201, registration.text
    created_user = registration.json()
    assert created_user["role"] == "school_admin"
    assert created_user["email"] == "admin@northschool.example.com"

    token_response = await client.post(
        "/api/v1/auth/token",
        data={
            "username": "admin@northschool.example.com",
            "password": "correct-horse-battery-staple",
        },
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    current_user = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert current_user.status_code == 200
    assert current_user.json()["id"] == created_user["id"]
    assert current_user.json()["school_id"] == created_user["school_id"]


@pytest.mark.asyncio
async def test_duplicate_school_slug_is_rejected(client: AsyncClient) -> None:
    payload = registration_payload()
    first = await client.post("/api/v1/auth/register", json=payload)
    duplicate = await client.post(
        "/api/v1/auth/register",
        json={
            **payload,
            "email": "another-admin@northschool.example.com",
        },
    )

    assert first.status_code == 201, first.text
    assert duplicate.status_code == 409


@pytest.mark.asyncio
async def test_current_user_requires_a_valid_access_token(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_rejects_a_wrong_password(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=registration_payload())
    response = await client.post(
        "/api/v1/auth/token",
        data={
            "username": "admin@northschool.example.com",
            "password": "this-is-the-wrong-password",
        },
    )

    assert response.status_code == 401


def test_production_settings_reject_the_placeholder_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="Set a generated JWT_SECRET_KEY"):
        Settings(
            app_env="production",
            jwt_secret_key=SecretStr(
                "replace-with-a-random-secret-of-at-least-32-characters"
            ),
        )


@pytest.mark.asyncio
async def test_ai_jobs_cannot_be_read_by_a_different_school_or_user(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enqueued: list[str] = []
    monkeypatch.setattr(
        "app.api.ai.celery_app.send_task",
        lambda _name, args, task_id: enqueued.append(task_id),
    )

    first_payload = registration_payload()
    await client.post("/api/v1/auth/register", json=first_payload)
    first_token = await client.post(
        "/api/v1/auth/token",
        data={"username": first_payload["email"], "password": first_payload["password"]},
    )
    created_job = await client.post(
        "/api/v1/ai/ask",
        json={"question": "What are the school rules?"},
        headers={"Authorization": f"Bearer {first_token.json()['access_token']}"},
    )

    second_payload = {
        **registration_payload(),
        "school_name": "South School",
        "school_slug": "south-school",
        "email": "admin@southschool.example.com",
    }
    await client.post("/api/v1/auth/register", json=second_payload)
    second_token = await client.post(
        "/api/v1/auth/token",
        data={"username": second_payload["email"], "password": second_payload["password"]},
    )
    foreign_job = await client.get(
        f"/api/v1/ai/jobs/{created_job.json()['id']}",
        headers={"Authorization": f"Bearer {second_token.json()['access_token']}"},
    )

    assert created_job.status_code == 202
    assert enqueued == [created_job.json()["id"]]
    assert foreign_job.status_code == 404
