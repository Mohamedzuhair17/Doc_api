import axios from "axios";

const DEFAULT_API_URL = "https://doc-api-efwm.onrender.com";
const rawApiUrl = (import.meta.env.VITE_API_URL || "").trim();
const isAbsoluteUrl = /^https?:\/\//i.test(rawApiUrl);
const API_URL = (isAbsoluteUrl ? rawApiUrl : DEFAULT_API_URL).replace(/\/+$/, "");
const API_KEY = (import.meta.env.VITE_API_KEY || "").trim();

const headers: Record<string, string> = {};
if (API_KEY) {
  headers["x-api-key"] = API_KEY;
}

const apiClient = axios.create({
  baseURL: API_URL,
  headers,
});

export interface UploadResponse {
  status: "success";
  fileName: string;
  summary: string;
  entities: {
    names: string[];
    organizations: string[];
    dates: string[];
    amounts: string[];
  };
  sentiment: string;
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
  const fileBase64 = await fileToBase64(file);
  const fileType = inferFileType(file);
  const payload = {
    fileName: file.name,
    fileType,
    fileBase64,
  };

  const { data } = await apiClient.post<UploadResponse>("/api/document-analyze", payload, {
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
  return data;
};

export default apiClient;
