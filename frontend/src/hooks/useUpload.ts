import { useMutation } from "@tanstack/react-query";
import { uploadDocument } from "@/services/apiClient";
import { useUIStore } from "@/store/uiStore";
import { toast } from "sonner";
import axios from "axios";

const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail
        .map((item) => (typeof item === "string" ? item : item?.msg))
        .filter(Boolean)
        .join(", ");
    }
  }

  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  return "Please try again.";
};

export const useUpload = () => {
  const { setCurrentFile, updateFileProgress, setFileStatus, setAnalysisResult } =
    useUIStore();

  const mutation = useMutation({
    mutationFn: (file: File) => {
      setCurrentFile({
        file,
        progress: 0,
        status: "uploading",
      });
      return uploadDocument(file, (progress) => {
        updateFileProgress(progress);
      });
    },
    onSuccess: (data) => {
      setFileStatus("uploaded");
      setAnalysisResult(data);
      toast.success("Document uploaded successfully", {
        description: `Analysis completed for ${data.fileName}`,
      });
    },
    onError: (error: unknown) => {
      const message = getErrorMessage(error);
      setFileStatus("error", message);
      toast.error("Upload failed", {
        description: message,
      });
    },
  });

  return {
    upload: mutation.mutate,
    isUploading: mutation.isPending,
    retry: () => {
      const file = useUIStore.getState().currentFile?.file;
      if (file) mutation.mutate(file);
    },
    cancel: () => {
      setFileStatus("idle");
    },
  };
};
