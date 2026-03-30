import type { JobStatusResponse } from "../types/job";

interface JobProgressProps {
  job: JobStatusResponse | null;
  onCancel: (() => void) | null;
  isCanceling?: boolean;
}

export function JobProgress({ job, onCancel, isCanceling = false }: JobProgressProps) {
  if (!job) {
    return (
      <section className="status-card">
        <h2>Status do processamento</h2>
        <p>Preparando o grimorio para traducao...</p>
        <div className="mana-bar">
          <span className="mana-orb" aria-hidden="true" />
          <div className="progress-track" role="progressbar" aria-valuenow={0}>
            <div className="progress-fill" style={{ width: "8%" }} />
            <span className="mana-percent">...</span>
          </div>
        </div>
      </section>
    );
  }

  const canCancel = job.status === "processing" && Boolean(onCancel);

  return (
    <section className="status-card">
      <h2>Status do processamento</h2>
      <p>
        Job: <strong>{job.job_id}</strong>
      </p>
      <p>
        Estado: <strong>{job.status}</strong>
      </p>
      <p>{job.message}</p>
      <div className="mana-bar">
        <span className="mana-orb" aria-hidden="true" />
        <div className="progress-track" role="progressbar" aria-valuenow={job.progress}>
          <div className="progress-fill" style={{ width: `${job.progress}%` }} />
          <span className="mana-percent">{job.progress}%</span>
        </div>
      </div>

      <p className="hint translation-meta">
        Traducao: <strong>{job.translation_progress}%</strong> ({job.translation_done}/{job.translation_total})
        {" - faltam "}
        <strong>{job.translation_remaining}</strong>
      </p>

      <div className="mana-bar translation-bar">
        <span className="mana-orb translation-orb" aria-hidden="true" />
        <div className="progress-track" role="progressbar" aria-valuenow={job.translation_progress}>
          <div className="progress-fill translation-fill" style={{ width: `${job.translation_progress}%` }} />
          <span className="mana-percent">{job.translation_progress}%</span>
        </div>
      </div>

      {canCancel ? (
        <button type="button" className="cancel-button" onClick={onCancel!} disabled={isCanceling}>
          {isCanceling ? "Cancelando..." : "Cancelar job"}
        </button>
      ) : null}

      {job.error ? <p className="error">{job.error}</p> : null}
    </section>
  );
}
