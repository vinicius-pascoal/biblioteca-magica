export type JobStatus = "processing" | "done" | "failed" | "canceled";

export interface JobCreateResponse {
  job_id: string;
  status: JobStatus;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  translation_progress: number;
  translation_done: number;
  translation_total: number;
  translation_remaining: number;
  message: string;
  source_language?: string | null;
  error?: string | null;
}

export interface JobCancelResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface ChapterPreview {
  id: string;
  title: string;
  item_count: number;
  excerpt: string;
}

export interface JobChaptersResponse {
  job_id: string;
  status: JobStatus;
  source_language?: string | null;
  target_language?: string | null;
  chapters: ChapterPreview[];
}
