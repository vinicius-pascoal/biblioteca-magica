from __future__ import annotations

from pathlib import Path

import fitz


class PDFService:
    @staticmethod
    def validate_pdf(file_name: str, payload: bytes) -> None:
        if not file_name.lower().endswith(".pdf"):
            raise ValueError("Apenas arquivos .pdf sao aceitos")

        if len(payload) < 4 or not payload.startswith(b"%PDF"):
            raise ValueError("Arquivo nao parece ser um PDF valido")

    @staticmethod
    def get_pdf_metadata(pdf_path: Path) -> dict:
        with fitz.open(pdf_path) as doc:
            metadata = doc.metadata or {}
            return {
                "title": metadata.get("title") or pdf_path.stem,
                "author": metadata.get("author") or "Desconhecido",
                "page_count": len(doc),
            }
