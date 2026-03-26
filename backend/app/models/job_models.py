from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Job:
    job_id: str
    filename: str
    input_pdf_path: Path
    status: str = "processing"
    progress: int = 0
    translation_progress: int = 0
    translation_done: int = 0
    translation_total: int = 0
    message: str = "Job criado"
    source_language: str | None = None
    epub_path: Path | None = None
    error: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    def touch(
        self,
        *,
        status: str | None = None,
        progress: int | None = None,
        translation_progress: int | None = None,
        translation_done: int | None = None,
        translation_total: int | None = None,
        message: str | None = None,
        error: str | None = None,
    ) -> None:
        if status is not None:
            self.status = status
        if progress is not None:
            self.progress = progress
        if translation_progress is not None:
            self.translation_progress = translation_progress
        if translation_done is not None:
            self.translation_done = translation_done
        if translation_total is not None:
            self.translation_total = translation_total
        if message is not None:
            self.message = message
        if error is not None:
            self.error = error
        self.updated_at = datetime.now(timezone.utc)
