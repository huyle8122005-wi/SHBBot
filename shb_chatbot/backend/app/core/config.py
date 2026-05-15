"""Application configuration using Pydantic BaseSettings."""
# ruff: noqa: I001 - Imports structured for Jinja2 template conditionals

from pathlib import Path
from typing import Literal

import pydantic
from pydantic import computed_field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path | None:
    """Find .env file in current or parent directories."""
    current = Path.cwd()
    for path in [current, current.parent]:
        env_file = path / ".env"
        if env_file.exists():
            return env_file
    return None


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_ignore_empty=True,
        extra="ignore",
    )

    # === Project ===
    PROJECT_NAME: str = "shb_chatbot"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "local", "staging", "production"] = "local"
    TIMEZONE: str = "UTC"  # IANA timezone (e.g. "UTC", "Europe/Warsaw", "America/New_York")
    MODELS_CACHE_DIR: Path = Path("./models_cache")
    MEDIA_DIR: Path = Path("./media")
    MAX_UPLOAD_SIZE_MB: int = 50  # Max file upload size in MB

    # === Logfire ===
    LOGFIRE_TOKEN: str | None = None
    LOGFIRE_SERVICE_NAME: str = "shb_chatbot"
    LOGFIRE_ENVIRONMENT: str = "development"

    # === Database (PostgreSQL async) ===
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "shb_chatbot"

    # Allow overriding full URLs from environment
    DATABASE_URL_OVERRIDE: str | None = pydantic.Field(default=None, alias="DATABASE_URL")
    DATABASE_URL_SYNC_OVERRIDE: str | None = pydantic.Field(default=None, alias="DATABASE_URL_SYNC")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        """Build async PostgreSQL connection URL."""
        if self.DATABASE_URL_OVERRIDE:
            url = self.DATABASE_URL_OVERRIDE
        else:
            from urllib.parse import quote_plus
            encoded_password = quote_plus(self.POSTGRES_PASSWORD)
            url = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{encoded_password}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # Add SSL requirement for Supabase if not already present
        if "supabase.co" in url and "ssl=" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}ssl=require"

        return url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Build sync PostgreSQL connection URL (for Alembic)."""
        if self.DATABASE_URL_SYNC_OVERRIDE:
            url = self.DATABASE_URL_SYNC_OVERRIDE
        else:
            from urllib.parse import quote_plus
            encoded_password = quote_plus(self.POSTGRES_PASSWORD)
            url = (
                f"postgresql://{self.POSTGRES_USER}:{encoded_password}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # Add SSL requirement for Supabase if not already present
        if "supabase.co" in url and "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}sslmode=require"

        return url

    # Pool configuration
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # === Auth (SECRET_KEY for JWT/Session/Admin) ===
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    SUPABASE_JWT_SECRET: str | None = "oQKNGiMU5qhoQdo6xWkJc/bsCUiaMDd+bBR6icsraOn2r+AVv+tgan5jM8RrAkRW1ojAIM4EdW/iltNLvCbQXw=="
    SUPABASE_URL: str | None = "https://aehzparpmmjdzpxkuwic.supabase.co"
    SUPABASE_ANON_KEY: str | None = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlaHpwYXJwbW1qZHpweGt1d2ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg0MzcyNTAsImV4cCI6MjA5NDAxMzI1MH0.89q-QUjJRLsoQvJMS0wjZOUkt13c8wa_M_uavpwYp6E"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate SECRET_KEY is secure in production."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        # Get environment from values if available
        env = info.data.get("ENVIRONMENT", "local") if info.data else "local"
        if v == "change-me-in-production-use-openssl-rand-hex-32" and env == "production":
            raise ValueError(
                "SECRET_KEY must be changed in production! "
                "Generate a secure key with: openssl rand -hex 32"
            )
        return v

    # === JWT Settings ===
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # === Auth (API Key) ===
    API_KEY: str = "change-me-in-production"
    API_KEY_HEADER: str = "X-API-Key"

    @field_validator("API_KEY")
    @classmethod
    def validate_api_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate API_KEY is set in production."""
        env = info.data.get("ENVIRONMENT", "local") if info.data else "local"
        if v == "change-me-in-production" and env == "production":
            raise ValueError(
                "API_KEY must be changed in production! "
                "Generate a secure key with: openssl rand -hex 32"
            )
        return v

    # === Redis ===
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0

    # Allow overriding full Redis URL from environment
    REDIS_URL_OVERRIDE: str | None = pydantic.Field(default=None, alias="REDIS_URL")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> str:
        """Build Redis connection URL."""
        if self.REDIS_URL_OVERRIDE:
            return self.REDIS_URL_OVERRIDE
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # === Celery ===
    CELERY_BROKER_URL_OVERRIDE: str | None = pydantic.Field(default=None, alias="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND_OVERRIDE: str | None = pydantic.Field(default=None, alias="CELERY_RESULT_BACKEND")

    @computed_field # type: ignore[prop-decorator]
    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.CELERY_BROKER_URL_OVERRIDE or self.REDIS_URL

    @computed_field # type: ignore[prop-decorator]
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.CELERY_RESULT_BACKEND_OVERRIDE or self.REDIS_URL

    # === AI Agent (pydantic_ai, openai/gemini) ===
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    AI_MODEL: str = "gemini-2.5-flash"
    AI_TEMPERATURE: float = 0.7
    AI_AVAILABLE_MODELS: list[str] = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gpt-5.4",
        "gpt-5.4-mini",
        "gpt-5.4-nano",
        "gpt-5-mini",
        "gpt-5-nano",
        "gpt-5",
        "gpt-5.1",
        "gpt-5.2",
        "o4-mini",
        "o3",
        "o3-mini",
        "gpt-4.1-mini",
        "gpt-4.1",
        "gpt-4.1-nano",
        "gpt-4o",
        "gpt-4o-mini",
    ]
    AI_FRAMEWORK: str = "pydantic_ai"
    LLM_PROVIDER: str = "openai"

    # === VNStock ===
    VNSTOCK_API_KEY: str = ""

    # === CORS ===
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://shbbot.pages.dev",
        "https://shbbot.onrender.com",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Assemble CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        elif isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v  # type: ignore[return-value]


settings = Settings()
