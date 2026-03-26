from __future__ import annotations

from pathlib import Path

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
                    tag = "h2" if item_type == "heading" else "p"
                    body_parts.append(f"<{tag}>{_escape_html(text)}</{tag}>")
                elif item_type == "image":
                    img_path = Path(item.get("path", ""))
                    if not img_path.exists():
                        continue
                    img_name = f"images/{img_path.name}"
                    image_item = epub.EpubItem(
                        uid=f"img-{img_path.stem}",
                        file_name=img_name,
                        media_type=f"image/{img_path.suffix.replace('.', '') or 'png'}",
                        content=img_path.read_bytes(),
                    )
                    book.add_item(image_item)
                    body_parts.append(
                        f'<figure><img src="{img_name}" alt="Imagem extraida"/></figure>')
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
