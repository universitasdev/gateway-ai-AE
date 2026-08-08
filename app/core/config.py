"""
Application settings loaded from environment variables.

Uses pydantic-settings to validate and type-cast all config values
at startup so misconfigurations fail fast.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration sourced from .env / environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Google Cloud ────────────────────────────────────────────
    project_id: str = "agente-acta-de-entrega"
    location: str = "us-east1"
    reasoning_engine_id: str = "6284579765949038592"  # full resource name or numeric ID

    # ── Telegram ────────────────────────────────────────────────
    telegram_bot_token: str = ""

    # ── WhatsApp (Meta Cloud API) ───────────────────────────────
    whatsapp_access_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_phone_number_id: str = ""

    # ── Application ─────────────────────────────────────────────
    log_level: str = "INFO"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()
