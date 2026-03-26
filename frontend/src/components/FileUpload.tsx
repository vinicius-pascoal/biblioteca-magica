import { useState, type ChangeEvent, type FormEvent } from "react";

interface FileUploadProps {
  disabled?: boolean;
  onSubmit: (file: File) => Promise<void>;
}

export function FileUpload({ disabled, onSubmit }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setFile(event.target.files?.[0] ?? null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError("Selecione um arquivo PDF para continuar.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("O arquivo precisa ser .pdf.");
      return;
    }

    setError(null);
    await onSubmit(file);
  };

  return (
    <form className="upload-card" onSubmit={handleSubmit}>
      <label htmlFor="pdf-file" className="upload-label">
        Arquivo PDF
      </label>
      <input
        id="pdf-file"
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
        disabled={disabled}
      />

      {file ? <p className="hint">Selecionado: {file.name}</p> : null}
      {error ? <p className="error">{error}</p> : null}

      <button type="submit" disabled={disabled}>
        Converter para EPUB em pt-BR
      </button>
    </form>
  );
}
