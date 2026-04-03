import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "";

const headers: Record<string, string> = {};
if (API_KEY) {
  headers["x-api-key"] = API_KEY;
}

const apiClient = axios.create({
  baseURL: API_URL,
  headers,
});

export interface UploadResponse {
  task_id: string;
  status: "queued";
}

export interface TaskStatus {
  task_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  result?: ExtractionResult;
  error?: string;
}

export interface ExtractionResult {
  summary: string;
  entities: {
    names: string[];
    organizations: string[];
    dates: string[];
    amounts: string[];
  };
  sentiment: string;
}

const fileToBase64 = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      if (typeof reader.result === "string") {
        resolve(reader.result.split(",")[1]);
      } else {
        reject(new Error("Failed to read file"));
      }
    };
    reader.onerror = (error) => reject(error);
  });

const inferFileType = (file: File): "pdf" | "docx" | "image" => {
  const ext = file.name.split(".").pop()?.toLowerCase() || "";
  if (ext === "pdf") return "pdf";
  if (ext === "docx") return "docx";
  return "image";
};

export const uploadDocument = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post<UploadResponse>("/api/document-analyze", formData, {
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
  return data;
};

export const getTaskStatus = async (taskId: string): Promise<TaskStatus> => {
  const { data } = await apiClient.get<TaskStatus>(`/api/task/${taskId}`);
  return data;
};

export default apiClient;
