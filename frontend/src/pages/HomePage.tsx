import { useEffect, useMemo, useState } from "react";

import { ChapterPreview } from "../components/ChapterPreview";
import { DownloadCard } from "../components/DownloadCard";
import { FileUpload } from "../components/FileUpload";
import { JobProgress } from "../components/JobProgress";
import { useJobStatus } from "../hooks/useJobStatus";
import { createJob, getDownloadUrl, getJobChapters } from "../services/api";
import type { ChapterPreview as ChapterPreviewItem } from "../types/job";

export function HomePage() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [chapters, setChapters] = useState<ChapterPreviewItem[]>([]);
  const [previewSourceLang, setPreviewSourceLang] = useState<string | null>(null);
  const [previewTargetLang, setPreviewTargetLang] = useState<string | null>(null);

  const { job, isLoading } = useJobStatus(jobId);
  const isFailed = job?.status === "failed";
  const isDone = job?.status === "done";
  const hasActiveJob = Boolean(jobId) && !isDone && !isFailed;
  const isProcessing = isSending || hasActiveJob;
  const canUpload = !isSending && (!jobId || isFailed);

  const downloadUrl = useMemo(() => {
    if (!jobId || job?.status !== "done") {
      return null;
    }
    return getDownloadUrl(jobId);
  }, [job, jobId]);

  useEffect(() => {
    if (!jobId) {
      setChapters([]);
      setPreviewSourceLang(null);
      setPreviewTargetLang(null);
      return;
    }

    let cancelled = false;

    const loadPreview = async () => {
      try {
        const preview = await getJobChapters(jobId);
        if (!cancelled) {
          setChapters(preview.chapters);
          setPreviewSourceLang(preview.source_language ?? null);
          setPreviewTargetLang(preview.target_language ?? null);
        }
      } catch {
        if (!cancelled) {
          setChapters([]);
        }
      }
    };

    loadPreview();

    return () => {
      cancelled = true;
    };
  }, [jobId, job?.progress, job?.status]);

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
      <header className="hero">
        <span className="hero-tag">TOMO ARCANO 8-BIT</span>
        <h1>Biblioteca Magica</h1>
        <p>Converta e traduza PDF para EPUB reflow em pt-BR com processamento local.</p>
      </header>

      {canUpload ? <FileUpload onSubmit={handleUpload} disabled={isSending || isLoading} /> : null}

      {submitError ? <p className="error">{submitError}</p> : null}

      {canUpload && isFailed ? <p className="error">{job.error || "Falha no processamento."}</p> : null}

      {isProcessing ? <JobProgress job={job} /> : null}

      {isDone ? (
        <ChapterPreview
          chapters={chapters}
          sourceLanguage={previewSourceLang ?? job?.source_language ?? null}
          targetLanguage={previewTargetLang}
        />
      ) : null}

      {isDone && downloadUrl ? <DownloadCard url={downloadUrl} /> : null}
    </main>
  );
}
