from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.core.paths import EPUB_DIR, EXTRACTED_DIR, INPUT_DIR, TEMP_DIR, TRANSLATED_DIR


class StorageService:
    def create_job_dirs(self, job_id: str) -> dict[str, Path]:
        paths = {
            "input": INPUT_DIR / job_id,
            "extracted": EXTRACTED_DIR / job_id,
            "translated": TRANSLATED_DIR / job_id,
            "epub": EPUB_DIR / job_id,
            "temp": TEMP_DIR / job_id,
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

    def cleanup_job_dirs(self, job_id: str, *, include_epub: bool = True) -> None:
        targets = [
            INPUT_DIR / job_id,
            EXTRACTED_DIR / job_id,
            TRANSLATED_DIR / job_id,
            TEMP_DIR / job_id,
        ]
        if include_epub:
            targets.append(EPUB_DIR / job_id)

        for path in targets:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)

    def cleanup_orphan_storage(self, ttl_hours: int) -> None:
        if ttl_hours <= 0:
            return

        cutoff_ts = datetime.now(timezone.utc).timestamp() - (ttl_hours * 3600)
        roots = [INPUT_DIR, EXTRACTED_DIR, TRANSLATED_DIR, EPUB_DIR, TEMP_DIR]

        for root in roots:
            if not root.exists():
                continue

            for child in root.iterdir():
                if not child.is_dir():
                    continue
                try:
                    mtime = child.stat().st_mtime
                except OSError:
                    continue
                if mtime < cutoff_ts:
                    shutil.rmtree(child, ignore_errors=True)
