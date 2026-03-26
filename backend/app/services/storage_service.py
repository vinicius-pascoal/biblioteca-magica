from __future__ import annotations

import shutil
from pathlib import Path

from app.core.paths import EPUB_DIR, EXTRACTED_DIR, INPUT_DIR, TRANSLATED_DIR


class StorageService:
    def create_job_dirs(self, job_id: str) -> dict[str, Path]:
        paths = {
            "input": INPUT_DIR / job_id,
            "extracted": EXTRACTED_DIR / job_id,
            "translated": TRANSLATED_DIR / job_id,
            "epub": EPUB_DIR / job_id,
        }
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
        return paths

    def save_uploaded_pdf(self, source_path: Path, target_dir: Path, filename: str) -> Path:
        target_path = target_dir / filename
        shutil.copy2(source_path, target_path)
        return target_path

    def save_upload_bytes(self, payload: bytes, target_dir: Path, filename: str) -> Path:
        target_path = target_dir / filename
        target_path.write_bytes(payload)
        return target_path
