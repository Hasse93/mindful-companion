"""Application configuration loaded from environment variables.

All settings have safe defaults so the API boots without a .env for local
development. Secrets (the Anthropic key) are read from the environment only and
are never committed — see .env.example.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Database ---
    database_url: str = "postgresql+psycopg://mindful:mindful@localhost:5432/mindful"

    # --- LLM provider ---
    # "gemini" (free tier, default) or "claude".
    llm_provider: str = "gemini"

    # Claude / Anthropic
    anthropic_api_key: str = ""
    chat_model: str = "claude-haiku-4-5-20251001"   # cheap default for dev
    report_model: str = "claude-haiku-4-5-20251001"
    # Set CHAT_MODEL=claude-opus-4-8 in .env for the polished demo.

    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # --- ML models (Hugging Face hub ids) ---
    emotion_model: str = "j-hartmann/emotion-english-distilroberta-base"
    sentiment_model: str = "distilbert-base-uncased-finetuned-sst-2-english"
    # When you fine-tune your own GoEmotions model, point emotion_model at the
    # local path or your HF repo id.

    # --- Auth (JWT) ---
    jwt_secret: str = "dev-only-change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # one week
    # Shared read-only demo account: reads allowed, writes blocked.
    demo_email: str = "demo@mindful.app"

    # --- App ---
    cors_origins: str = "http://localhost:3000"
    # Optional regex to allow a family of origins (e.g. all Vercel preview +
    # production URLs for the project). Empty = disabled.
    cors_origin_regex: str = ""
    # When true, ML + LLM calls return deterministic stubs (used by tests and
    # for booting the API with no model downloads / no API key).
    fake_ai: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
