import type { JobStatusResponse } from "../types/job";

interface JobProgressProps {
  job: JobStatusResponse | null;
}

export function JobProgress({ job }: JobProgressProps) {
  if (!job) {
    return null;
  }

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

      {job.error ? <p className="error">{job.error}</p> : null}
    </section>
  );
}
