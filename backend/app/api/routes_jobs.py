from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.paths import EXTRACTED_DIR, TRANSLATED_DIR
from app.models.job_models import Job
from app.schemas.job_schemas import ChapterPreview, JobChaptersResponse, JobCreateResponse, JobStatusResponse
from app.services.job_processor import JobProcessor
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/jobs", tags=["jobs"])

JOBS: dict[str, Job] = {}
PROCESSOR = JobProcessor()
STORAGE = StorageService()
PDF = PDFService()


def _process_job(job_id: str, paths: dict[str, Path]) -> None:
    job = JOBS[job_id]
    PROCESSOR.process(job, paths)


@router.post("", response_model=JobCreateResponse)
async def create_job(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> JobCreateResponse:
    payload = await file.read()
    filename = file.filename or "input.pdf"

    try:
        PDF.validate_pdf(filename, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job_id = uuid4().hex
    paths = STORAGE.create_job_dirs(job_id)
    input_pdf_path = STORAGE.save_upload_bytes(
        payload, paths["input"], filename)

    job = Job(job_id=job_id, filename=filename, input_pdf_path=input_pdf_path)
    JOBS[job_id] = job

    background_tasks.add_task(_process_job, job_id, paths)
    return JobCreateResponse(job_id=job_id, status=job.status)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nao encontrado")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        source_language=job.source_language,
        error=job.error,
    )


@router.get("/{job_id}/chapters", response_model=JobChaptersResponse)
def get_job_chapters(job_id: str) -> JobChaptersResponse:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nao encontrado")

    translated_path = TRANSLATED_DIR / job_id / "translated_content.json"
    extracted_path = EXTRACTED_DIR / job_id / "structured_content.json"

    source_path = translated_path if translated_path.exists() else extracted_path
    if not source_path.exists():
        return JobChaptersResponse(
            job_id=job.job_id,
            status=job.status,
            source_language=job.source_language,
            target_language=None,
            chapters=[],
        )

    structure = json.loads(source_path.read_text(encoding="utf-8"))
    chapter_previews: list[ChapterPreview] = []

    for chapter in structure.get("chapters", []):
        items = chapter.get("items", [])
        excerpt = ""
        for item in items:
            if item.get("type") in {"paragraph", "heading"}:
                excerpt = (item.get("translated_text")
                           or item.get("text") or "").strip()
                if excerpt:
                    break

        chapter_previews.append(
            ChapterPreview(
                id=chapter.get("id", ""),
                title=chapter.get("title", "Capitulo"),
                item_count=len(items),
                excerpt=excerpt[:220],
            )
        )

    return JobChaptersResponse(
        job_id=job.job_id,
        status=job.status,
        source_language=structure.get(
            "source_language") or job.source_language,
        target_language=structure.get("target_language"),
        chapters=chapter_previews,
    )


@router.get("/{job_id}/download")
def download_job(job_id: str) -> FileResponse:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nao encontrado")

    if job.status != "done" or not job.epub_path or not job.epub_path.exists():
        raise HTTPException(
            status_code=400, detail="EPUB ainda nao esta disponivel")

    return FileResponse(
        path=job.epub_path,
        filename=job.epub_path.name,
        media_type="application/epub+zip",
    )
