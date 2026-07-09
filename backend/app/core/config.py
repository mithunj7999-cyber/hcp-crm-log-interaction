"""
HCP CRM Backend — Configuration Module.

Loads environment variables and exposes them as a typed Pydantic settings object.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # ── Database ────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./hcp_crm.db"

    # ── Groq LLM ───────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    # Primary Groq model and optional fallback
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_FALLBACK_MODEL: str = "llama-3.3-70b-versatile"

    # ── App ─────────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent.parent / ".env"),
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env once)."""
    return Settings()
