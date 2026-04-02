import { useQuery } from "@tanstack/react-query";
import { getTaskStatus, type TaskStatus } from "@/services/apiClient";

export const usePolling = (taskId: string | null) => {
  return useQuery<TaskStatus>({
    queryKey: ["taskStatus", taskId],
    queryFn: () => getTaskStatus(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed") return false;
      return 2000;
    },
    retry: 3,
  });
};
