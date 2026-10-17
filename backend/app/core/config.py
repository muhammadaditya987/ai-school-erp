from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "School ERP API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = "postgresql+asyncpg://school_erp:change-this-local-password@localhost:5432/school_erp"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://school_erp:change-this-local-password@localhost:5672/"
    s3_endpoint_url: str | None = None
    s3_bucket: str = "school-erp"
    s3_region: str = "ap-southeast-1"
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    ai_provider: str = "openai"
    ai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-2.5-flash"
    ai_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    huggingface_api_token: SecretStr | None = None
    huggingface_model: str = "mistralai/Mistral-7B-Instruct-v0.3"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    chroma_persist_directory: str = "./data/chroma"
    chroma_host: str | None = None
    chroma_port: int = Field(default=8000, ge=1, le=65535)
    embedding_cache_directory: str = "./data/embedding-cache"
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("replace-with-a-random-secret-of-at-least-32-characters"),
        min_length=32,
    )
    jwt_access_token_expire_minutes: int = Field(default=15, ge=1, le=1440)
    mcp_access_token: SecretStr | None = None
    log_level: str = "INFO"

    @model_validator(mode="after")
    def require_production_jwt_secret(self) -> "Settings":
        if (
            self.app_env.casefold() in {"prod", "production"}
            and self.jwt_secret_key.get_secret_value().startswith("replace-with-")
        ):
            raise ValueError("Set a generated JWT_SECRET_KEY before using production mode")
        provider = self.ai_provider.casefold()
        if provider not in {"openai", "gemini", "ollama", "huggingface"}:
            raise ValueError("AI_PROVIDER must be openai, gemini, ollama, or huggingface")
        return self

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def normalize_service_urls(self) -> "Settings":
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )
        elif self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
