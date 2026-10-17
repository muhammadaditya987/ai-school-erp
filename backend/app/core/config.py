from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "School ERP API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://school_erp:change-this-local-password@localhost:5432/school_erp"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://school_erp:change-this-local-password@localhost:5672/"
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("replace-with-a-random-secret-of-at-least-32-characters"),
        min_length=32,
    )
    jwt_access_token_expire_minutes: int = Field(default=15, ge=1, le=1440)
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
