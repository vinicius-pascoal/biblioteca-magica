from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
STORAGE_DIR = BASE_DIR / "storage"
INPUT_DIR = STORAGE_DIR / "input"
EXTRACTED_DIR = STORAGE_DIR / "extracted"
TRANSLATED_DIR = STORAGE_DIR / "translated"
EPUB_DIR = STORAGE_DIR / "epub"
TEMP_DIR = STORAGE_DIR / "temp"


def ensure_storage_dirs() -> None:
    for path in [
        STORAGE_DIR,
        INPUT_DIR,
        EXTRACTED_DIR,
        TRANSLATED_DIR,
        EPUB_DIR,
        TEMP_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
