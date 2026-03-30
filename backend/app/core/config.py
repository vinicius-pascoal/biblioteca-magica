from __future__ import annotations

import os

from pydantic import BaseModel


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Biblioteca Magica API")
    libretranslate_url: str = os.getenv(
        "LIBRETRANSLATE_URL", "http://127.0.0.1:5000/translate")
    source_language: str = os.getenv("SOURCE_LANGUAGE", "en")
    target_language: str = os.getenv("TARGET_LANGUAGE", "pt")
    max_translate_chunk_size: int = _get_int_env(
        "MAX_TRANSLATE_CHUNK_SIZE", 1800)
    job_ttl_hours: int = _get_int_env("JOB_TTL_HOURS", 24)
    cleanup_interval_minutes: int = _get_int_env(
        "CLEANUP_INTERVAL_MINUTES", 15)


settings = Settings()
