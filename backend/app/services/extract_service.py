from __future__ import annotations

import json
import re
from pathlib import Path

import fitz


def _cleanup_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _is_heading(text: str, avg_size: float) -> bool:
    words = text.split()
    if not words:
        return False
    if avg_size >= 14:
        return True
    if len(words) <= 8 and text == text.title():
        return True
    return False


class ExtractService:
    @staticmethod
    def _split_into_chapters(items: list[dict]) -> list[dict]:
        # Mantem estrutura continua sem separadores por heading.
        return [
            {
                "id": "chapter-1",
                "title": "Conteudo",
                "items": items,
            }
        ]

    def extract(self, pdf_path: Path, extracted_dir: Path) -> dict:
        extracted_dir.mkdir(parents=True, exist_ok=True)
        flat_items: list[dict] = []

        with fitz.open(pdf_path) as doc:
            for page_idx, page in enumerate(doc, start=1):
                text_blocks = page.get_text("dict").get("blocks", [])
                ordered_text_blocks = sorted(
                    [b for b in text_blocks if b.get("type") == 0],
                    key=lambda b: (round(b["bbox"][1], 1),
                                   round(b["bbox"][0], 1)),
                )

                for block_idx, block in enumerate(ordered_text_blocks, start=1):
                    lines = block.get("lines", [])
                    segments: list[str] = []
                    sizes: list[float] = []

                    for line in lines:
                        for span in line.get("spans", []):
                            txt = span.get("text", "")
                            if txt:
                                segments.append(txt)
                                sizes.append(float(span.get("size", 12)))

                    text = _cleanup_text(" ".join(segments))
                    if not text:
                        continue

                    avg_size = sum(sizes) / len(sizes) if sizes else 12
                    item_type = "heading" if _is_heading(
                        text, avg_size) else "paragraph"

                    flat_items.append(
                        {
                            "id": f"p-{page_idx}-{block_idx}",
                            "type": item_type,
                            "page": page_idx,
                            "text": text,
                            "translated_text": "",
                        }
                    )

                for img_idx, image_info in enumerate(page.get_images(full=True), start=1):
                    xref = image_info[0]
                    image = doc.extract_image(xref)
                    image_bytes = image["image"]
                    ext = image.get("ext", "png")
                    image_name = f"img_{page_idx:03d}_{img_idx:03d}.{ext}"
                    image_path = extracted_dir / image_name
                    image_path.write_bytes(image_bytes)

                    flat_items.append(
                        {
                            "id": f"img-{page_idx}-{img_idx}",
                            "type": "image",
                            "page": page_idx,
                            "path": str(image_path),
                            "caption": "",
                        }
                    )

        structure = {
            "title": pdf_path.stem,
            "source_language": "auto",
            "target_language": "pt-BR",
            "chapters": self._split_into_chapters(flat_items),
        }

        structure_path = extracted_dir / "structured_content.json"
        structure_path.write_text(
            json.dumps(structure, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return structure
