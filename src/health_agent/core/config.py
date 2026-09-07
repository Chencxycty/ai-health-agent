from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    llm_api_key: str = Field(repr=False)
    llm_base_url: str
    llm_model: str

    llm_temperature: float = 0.2
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
