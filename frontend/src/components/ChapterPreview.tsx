import type { ChapterPreview as ChapterPreviewItem } from "../types/job";

interface ChapterPreviewProps {
  sourceLanguage?: string | null;
  targetLanguage?: string | null;
  chapters: ChapterPreviewItem[];
}

export function ChapterPreview({ sourceLanguage, targetLanguage, chapters }: ChapterPreviewProps) {
  if (!chapters.length) {
    return null;
  }

  return (
    <section className="chapter-preview-card">
      <h2>Preview de capitulos</h2>
      <p className="hint">
        Idioma detectado: <strong>{sourceLanguage || "desconhecido"}</strong>
        {targetLanguage ? (
          <>
            {" "}
            {"-> "}
            <strong>{targetLanguage}</strong>
          </>
        ) : null}
      </p>

      <div className="chapter-list">
        {chapters.map((chapter) => (
          <article key={chapter.id} className="chapter-item">
            <h3>{chapter.title}</h3>
            <p className="hint">{chapter.item_count} blocos</p>
            {chapter.excerpt ? <p>{chapter.excerpt}</p> : <p className="hint">Sem trecho textual.</p>}
          </article>
        ))}
      </div>
    </section>
  );
}
