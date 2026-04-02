import { create } from "zustand";

interface UploadedFile {
  file: File;
  taskId?: string;
  progress: number;
  status: "idle" | "uploading" | "uploaded" | "error";
  error?: string;
}

interface UIState {
  currentFile: UploadedFile | null;
  activeTaskId: string | null;
  activeTab: string;
  setCurrentFile: (file: UploadedFile | null) => void;
  setActiveTaskId: (id: string | null) => void;
  setActiveTab: (tab: string) => void;
  updateFileProgress: (progress: number) => void;
  setFileStatus: (status: UploadedFile["status"], error?: string) => void;
  setFileTaskId: (taskId: string) => void;
  reset: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  currentFile: null,
  activeTaskId: null,
  activeTab: "text",
  setCurrentFile: (file) => set({ currentFile: file }),
  setActiveTaskId: (id) => set({ activeTaskId: id }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  updateFileProgress: (progress) =>
    set((s) => ({
      currentFile: s.currentFile ? { ...s.currentFile, progress } : null,
    })),
  setFileStatus: (status, error) =>
    set((s) => ({
      currentFile: s.currentFile ? { ...s.currentFile, status, error } : null,
    })),
  setFileTaskId: (taskId) =>
    set((s) => ({
      currentFile: s.currentFile ? { ...s.currentFile, taskId } : null,
      activeTaskId: taskId,
    })),
  reset: () => set({ currentFile: null, activeTaskId: null, activeTab: "text" }),
}));
