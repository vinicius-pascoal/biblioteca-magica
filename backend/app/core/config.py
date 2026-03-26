from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Biblioteca Magica API"
    libretranslate_url: str = "http://127.0.0.1:5000/translate"
    source_language: str = "en"
    target_language: str = "pt"
    max_translate_chunk_size: int = 1800


settings = Settings()
