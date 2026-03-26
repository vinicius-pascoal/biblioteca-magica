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
    message: str = "Job criado"
    epub_path: Path | None = None
    error: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    def touch(self, *, status: str | None = None, progress: int | None = None, message: str | None = None, error: str | None = None) -> None:
        if status is not None:
            self.status = status
        if progress is not None:
            self.progress = progress
        if message is not None:
            self.message = message
        if error is not None:
            self.error = error
        self.updated_at = datetime.now(timezone.utc)
