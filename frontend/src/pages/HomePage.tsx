import { useMemo, useState } from "react";

import { DownloadCard } from "../components/DownloadCard";
import { FileUpload } from "../components/FileUpload";
import { JobProgress } from "../components/JobProgress";
import { useJobStatus } from "../hooks/useJobStatus";
import { createJob, getDownloadUrl } from "../services/api";

export function HomePage() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  const { job, isLoading } = useJobStatus(jobId);

  const downloadUrl = useMemo(() => {
    if (!jobId || job?.status !== "done") {
      return null;
    }
    return getDownloadUrl(jobId);
  }, [job, jobId]);

  const handleUpload = async (file: File) => {
    setSubmitError(null);
    setIsSending(true);
    try {
      const created = await createJob(file);
      setJobId(created.job_id);
    } catch {
      setSubmitError("Falha ao enviar arquivo para o backend.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <main className="container">
      <header>
        <h1>Biblioteca Magica</h1>
        <p>Converta e traduza PDF para EPUB reflow em pt-BR com processamento local.</p>
      </header>

      <FileUpload onSubmit={handleUpload} disabled={isSending || isLoading} />

      {submitError ? <p className="error">{submitError}</p> : null}

      <JobProgress job={job} />

      {downloadUrl ? <DownloadCard url={downloadUrl} /> : null}
    </main>
  );
}
