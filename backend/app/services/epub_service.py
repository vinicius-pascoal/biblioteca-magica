from __future__ import annotations

from pathlib import Path
import re
import zipfile

from ebooklib import epub


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


class EpubService:
    def build_epub(self, structure: dict, output_path: Path, title: str, author: str) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        book = epub.EpubBook()
        book.set_identifier("biblioteca-magica-generated")
        book.set_title(title)
        book.set_language("pt-BR")
        book.add_author(author)

        cover_defined = False

        chapters = []
        for chapter_idx, chapter_data in enumerate(structure.get("chapters", []), start=1):
            chapter_title = chapter_data.get(
                "title") or f"Capitulo {chapter_idx}"
            file_name = f"chap_{chapter_idx}.xhtml"
            chapter = epub.EpubHtml(
                title=chapter_title, file_name=file_name, lang="pt-BR")

            body_parts = [f"<h1>{_escape_html(chapter_title)}</h1>"]
            for item in chapter_data.get("items", []):
                item_type = item.get("type")
                if item_type in {"paragraph", "heading"}:
                    text = item.get("translated_text") or item.get("text", "")
                    if not text:
                        continue
                    source_id = _escape_html(str(item.get("id", "")))
                    tag = "h2" if item_type == "heading" else "p"
                    body_parts.append(
                        f"<{tag} data-source-id=\"{source_id}\">{_escape_html(text)}</{tag}>"
                    )
                elif item_type == "image":
                    img_path = Path(item.get("path", ""))
                    if not img_path.exists():
                        continue
                    source_id = _escape_html(str(item.get("id", "")))
                    ext = img_path.suffix.replace(".", "").lower() or "png"
                    img_name = f"images/{img_path.name}"
                    image_item = epub.EpubItem(
                        uid=f"img-{img_path.stem}",
                        file_name=img_name,
                        media_type=f"image/{ext}",
                        content=img_path.read_bytes(),
                    )
                    book.add_item(image_item)

                    if not cover_defined:
                        book.set_cover(f"cover.{ext}", img_path.read_bytes())
                        cover_defined = True

                    body_parts.append(
                        f'<figure data-source-id="{source_id}"><img src="{img_name}" alt="Imagem extraida"/></figure>')
                    caption = item.get("caption", "").strip()
                    if caption:
                        body_parts.append(
                            f"<figcaption>{_escape_html(caption)}</figcaption>")

            chapter.content = "\n".join(body_parts)
            book.add_item(chapter)
            chapters.append(chapter)

        if not chapters:
            fallback = epub.EpubHtml(
                title="Conteudo", file_name="chap_1.xhtml", lang="pt-BR")
            fallback.content = "<p>Nenhum conteudo disponivel.</p>"
            book.add_item(fallback)
            chapters.append(fallback)

        book.toc = tuple(chapters)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ["nav", *chapters]

        epub.write_epub(str(output_path), book)
        return output_path

    def validate_epub_content(self, structure: dict, epub_path: Path) -> None:
        expected_ids: set[str] = set()

        for chapter in structure.get("chapters", []):
            for item in chapter.get("items", []):
                item_id = str(item.get("id", "")).strip()
                if not item_id:
                    continue

                item_type = item.get("type")
                if item_type in {"paragraph", "heading"}:
                    has_text = bool((item.get("translated_text")
                                    or item.get("text", "")).strip())
                    if has_text:
                        expected_ids.add(item_id)
                elif item_type == "image":
                    expected_ids.add(item_id)

        found_ids: set[str] = set()
        with zipfile.ZipFile(epub_path, "r") as archive:
            html_names = [
                name
                for name in archive.namelist()
                if name.lower().endswith((".xhtml", ".html", ".htm"))
            ]

            for name in html_names:
                html = archive.read(name).decode("utf-8", errors="ignore")
                matches = re.findall(r'data-source-id="([^"]+)"', html)
                found_ids.update(matches)

        missing_ids = sorted(expected_ids - found_ids)
        if missing_ids:
            preview = ", ".join(missing_ids[:10])
            if len(missing_ids) > 10:
                preview += ", ..."
            raise ValueError(
                "EPUB incompleto: nem todo o conteudo do PDF original foi preservado. "
                f"Itens ausentes: {preview}"
            )
