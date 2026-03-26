from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.models.job_models import Job
from app.schemas.job_schemas import JobCreateResponse, JobStatusResponse
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
        error=job.error,
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
