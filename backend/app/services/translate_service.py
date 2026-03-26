from __future__ import annotations

import time

import requests

from app.core.config import settings


class TranslateService:
    def __init__(self) -> None:
        self.url = settings.libretranslate_url
        self.max_chunk = settings.max_translate_chunk_size

    def _translate_chunk(self, text: str, source: str, target: str) -> str:
        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text",
        }
        response = requests.post(self.url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("translatedText", text)

    def _safe_translate(self, text: str, source: str, target: str) -> str:
        if len(text) <= self.max_chunk:
            return self._translate_chunk(text, source, target)

        chunks = [text[i: i + self.max_chunk]
                  for i in range(0, len(text), self.max_chunk)]
        translated_chunks = [self._translate_chunk(
            chunk, source, target) for chunk in chunks]
        return "".join(translated_chunks)

    def translate_structure(self, structure: dict, source: str, target: str) -> tuple[dict, list[str]]:
        warnings: list[str] = []

        for chapter in structure.get("chapters", []):
            for item in chapter.get("items", []):
                if item.get("type") not in {"paragraph", "heading"}:
                    continue

                original = item.get("text", "")
                if not original:
                    item["translated_text"] = ""
                    continue

                translated = ""
                for attempt in range(1, 4):
                    try:
                        translated = self._safe_translate(
                            original, source=source, target=target)
                        break
                    except requests.RequestException:
                        if attempt == 3:
                            warnings.append(
                                f"Falha ao traduzir bloco {item.get('id')}; texto original sera usado"
                            )
                            translated = original
                        else:
                            time.sleep(0.8 * attempt)

                item["translated_text"] = translated

        return structure, warnings
