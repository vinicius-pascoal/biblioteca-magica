interface DownloadCardProps {
  url: string;
}

export function DownloadCard({ url }: DownloadCardProps) {
  return (
    <section className="download-card">
      <h2>EPUB pronto</h2>
      <p>Seu arquivo foi gerado. Clique para baixar.</p>
      <a href={url} className="download-button">
        Baixar EPUB
      </a>
    </section>
  );
}
