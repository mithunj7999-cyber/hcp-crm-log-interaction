"""
HCP CRM Backend — Configuration Module.

Loads environment variables and exposes them as a typed Pydantic settings object.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # ── Database ────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/hcp_crm"

    # ── Groq LLM ───────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""

    # ── App ─────────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env once)."""
    return Settings()
