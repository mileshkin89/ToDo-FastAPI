import os
from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent

api_version_prefix = "/api/v1"
admin_prefix = "/admin"
auth_prefix = "/auth"
analytics_prefix = "/analytics"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


def get_env_file() -> str:
    environment = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
    if environment == Environment.TESTING:
        return str(BASE_DIR / ".env.test")
    return str(BASE_DIR / ".env")


class Settings(BaseSettings):
    BASE_URL: str

    PASSWORD_HASH_SCHEME: str = "argon2"

    # PostgreSQL / Database
    POSTGRES_DB: str
    POSTGRES_DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str

    # JWT / Auth
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Reset password token / Auth
    RESET_TOKEN_TTL_MINUTES: int = 15

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # email service
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str

    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """Return database URL. Uses in-memory SQLite for testing."""
        environment = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)

        if environment == Environment.TESTING:
            return "sqlite+aiosqlite:///:memory:"

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_DB_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Return full Redis connection URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
