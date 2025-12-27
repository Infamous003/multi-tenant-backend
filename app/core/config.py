# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    App settings loaded from .env file.
    """

    APP_NAME: str = "Tenant Usage Backend"
    ENV: str = Field(default="development", description="development|staging|production")
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str

    ADMIN_API_KEY: str

    DEFAULT_MONTHLY_USAGE_LIMIT: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

settings = Settings()
