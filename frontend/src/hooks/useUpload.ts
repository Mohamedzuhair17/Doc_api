import { useMutation } from "@tanstack/react-query";
import { uploadDocument } from "@/services/apiClient";
import { useUIStore } from "@/store/uiStore";
import { toast } from "sonner";

export const useUpload = () => {
  const { setCurrentFile, updateFileProgress, setFileStatus, setFileTaskId } =
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
      setFileTaskId(data.task_id);
      toast.success("Document uploaded successfully", {
        description: `Task ID: ${data.task_id}`,
      });
    },
    onError: (error: Error) => {
      setFileStatus("error", error.message);
      toast.error("Upload failed", {
        description: error.message || "Please try again.",
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
