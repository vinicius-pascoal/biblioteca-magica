import axios from "axios";

import type {
  JobCancelResponse,
  JobChaptersResponse,
  JobCreateResponse,
  JobStatusResponse,
} from "../types/job";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
});

export async function createJob(file: File): Promise<JobCreateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<JobCreateResponse>("/jobs", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await api.get<JobStatusResponse>(`/jobs/${jobId}`);
  return response.data;
}

export async function cancelJob(jobId: string): Promise<JobCancelResponse> {
  const response = await api.post<JobCancelResponse>(`/jobs/${jobId}/cancel`);
  return response.data;
}

export async function getJobChapters(jobId: string): Promise<JobChaptersResponse> {
  const response = await api.get<JobChaptersResponse>(`/jobs/${jobId}/chapters`);
  return response.data;
}

export function getDownloadUrl(jobId: string): string {
  return `${api.defaults.baseURL}/jobs/${jobId}/download`;
}
