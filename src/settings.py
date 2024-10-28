from enum import StrEnum
from pydantic import BaseModel, Field, SecretStr
import os


class Mode(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

    @property
    def is_development(self) -> bool:
        return self == Mode.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self == Mode.PRODUCTION


class Settings:
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "user")
    POSTGRES_PASSWORD: SecretStr = SecretStr(
        os.environ.get("POSTGRES_PASSWORD", "password")
    )
    POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "example")

    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", "6379"))

    MODE: Mode = Mode(os.environ.get("MODE", "development"))

    JWT_SECRET: SecretStr = SecretStr(os.environ.get("JWT_SECRET", "jwt_secret"))
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", "10080")
    )
