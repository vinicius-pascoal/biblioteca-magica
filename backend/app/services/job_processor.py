from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings
from app.models.job_models import Job
from app.services.epub_service import EpubService
from app.services.extract_service import ExtractService
from app.services.pdf_service import PDFService
from app.services.translate_service import TranslateService


class JobProcessor:
    def __init__(self) -> None:
        self.pdf_service = PDFService()
        self.extract_service = ExtractService()
        self.translate_service = TranslateService()
        self.epub_service = EpubService()

    def process(self, job: Job, paths: dict[str, Path]) -> None:
        try:
            job.touch(progress=10, message="Lendo metadados do PDF")
            metadata = self.pdf_service.get_pdf_metadata(job.input_pdf_path)

            job.touch(progress=30, message="Extraindo texto e imagens")
            structure = self.extract_service.extract(
                job.input_pdf_path, paths["extracted"])

            job.touch(progress=45, message="Detectando idioma de origem")
            detected_source = self.translate_service.detect_source_language(
                structure, fallback=settings.source_language
            )
            structure["source_language"] = detected_source
            job.source_language = detected_source

            total_blocks = self.translate_service.count_translatable_blocks(
                structure)

            def on_translate_progress(done: int, total: int) -> None:
                pct = 0 if total == 0 else int((done / total) * 100)
                overall = 60 if total == 0 else 60 + int((done / total) * 24)
                remaining = max(total - done, 0)
                job.touch(
                    progress=overall,
                    translation_progress=pct,
                    translation_done=done,
                    translation_total=total,
                    message=f"Traduzindo conteudo ({pct}%) - faltam {remaining} blocos",
                )

            job.touch(
                progress=60,
                translation_progress=0,
                translation_done=0,
                translation_total=total_blocks,
                message="Traduzindo conteudo",
            )
            translated, warnings = self.translate_service.translate_structure(
                structure,
                source=detected_source,
                target=settings.target_language,
                progress_callback=on_translate_progress,
            )

            translated_path = paths["translated"] / "translated_content.json"
            translated_path.write_text(
                json.dumps(translated, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            job.touch(progress=85, message="Montando EPUB")
            epub_file = paths["epub"] / f"{job.input_pdf_path.stem}_ptbr.epub"
            self.epub_service.build_epub(
                structure=translated,
                output_path=epub_file,
                title=metadata.get("title") or job.input_pdf_path.stem,
                author=metadata.get("author") or "Desconhecido",
            )

            msg = "EPUB gerado com sucesso"
            if warnings:
                msg = f"EPUB gerado com avisos ({len(warnings)})"

            job.epub_path = epub_file
            job.touch(
                status="done",
                progress=100,
                translation_progress=100 if total_blocks > 0 else 0,
                translation_done=total_blocks,
                translation_total=total_blocks,
                message=msg,
            )
        except Exception as exc:
            job.touch(
                status="failed",
                progress=100,
                message="Falha no processamento",
                error=str(exc),
            )
