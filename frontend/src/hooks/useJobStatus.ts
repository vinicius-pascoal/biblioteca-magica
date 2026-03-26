import { useEffect, useState } from "react";

import { getJobStatus } from "../services/api";
import type { JobStatusResponse } from "../types/job";

export function useJobStatus(jobId: string | null) {
  const [job, setJob] = useState<JobStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!jobId) {
      setJob(null);
      return;
    }

    let timer: number | undefined;
    let cancelled = false;

    const poll = async () => {
      setIsLoading(true);
      try {
        const next = await getJobStatus(jobId);
        if (!cancelled) {
          setJob(next);
          if (next.status === "processing") {
            timer = window.setTimeout(poll, 1500);
          }
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timer) {
        window.clearTimeout(timer);
      }
    };
  }, [jobId]);

  return { job, isLoading };
}
