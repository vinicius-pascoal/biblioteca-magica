from __future__ import annotations

import time
from collections.abc import Callable

import requests
from langdetect import LangDetectException, detect

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

    @staticmethod
    def _normalize_lang(lang: str) -> str:
        normalized = (lang or "").strip().lower()
        aliases = {
            "pt-br": "pt",
            "pt-pt": "pt",
            "zh-cn": "zh",
            "zh-tw": "zh",
        }
        return aliases.get(normalized, normalized)

    def detect_source_language(self, structure: dict, fallback: str) -> str:
        samples: list[str] = []
        for chapter in structure.get("chapters", []):
            for item in chapter.get("items", []):
                if item.get("type") in {"paragraph", "heading"}:
                    text = item.get("text", "").strip()
                    if text:
                        samples.append(text)
                if len(samples) >= 10:
                    break
            if len(samples) >= 10:
                break

        sample_text = " ".join(samples)[:3000].strip()
        if len(sample_text) < 20:
            return self._normalize_lang(fallback)

        try:
            detected = detect(sample_text)
            return self._normalize_lang(detected)
        except LangDetectException:
            return self._normalize_lang(fallback)

    @staticmethod
    def count_translatable_blocks(structure: dict) -> int:
        total = 0
        for chapter in structure.get("chapters", []):
            for item in chapter.get("items", []):
                if item.get("type") in {"paragraph", "heading"}:
                    total += 1
        return total

    def translate_structure(
        self,
        structure: dict,
        source: str,
        target: str,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> tuple[dict, list[str]]:
        warnings: list[str] = []
        total = self.count_translatable_blocks(structure)
        done = 0

        if progress_callback is not None:
            progress_callback(done, total)

        for chapter in structure.get("chapters", []):
            for item in chapter.get("items", []):
                if item.get("type") not in {"paragraph", "heading"}:
                    continue

                original = item.get("text", "")
                if not original:
                    item["translated_text"] = ""
                    done += 1
                    if progress_callback is not None:
                        progress_callback(done, total)
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
                done += 1
                if progress_callback is not None:
                    progress_callback(done, total)

        return structure, warnings
