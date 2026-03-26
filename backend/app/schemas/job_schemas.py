from __future__ import annotations

from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    source_language: str | None = None
    error: str | None = None


class ChapterPreview(BaseModel):
    id: str
    title: str
    item_count: int
    excerpt: str


class JobChaptersResponse(BaseModel):
    job_id: str
    status: str
    source_language: str | None = None
    target_language: str | None = None
    chapters: list[ChapterPreview]
