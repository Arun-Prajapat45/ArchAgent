from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: str = "development"
    openrouter_api_key: str | None = Field(default=None, repr=False)
    infracost_api_key: str | None = Field(default=None, repr=False)
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"
    openrouter_embedding_model: str = "openai/text-embedding-3-small"
    cors_origins: list[str] = ["http://localhost:8501"]
    max_prompt_chars: int = Field(default=10_000, ge=1, le=100_000)
    external_timeout_seconds: float = Field(default=15.0, gt=0, le=120)
    critic_max_iterations: int = Field(default=3, ge=1, le=5)
    rate_limit_per_minute: int = Field(default=0, ge=0, le=10_000)

    @property
    def ready(self) -> bool:
        return bool(self.openrouter_api_key)
