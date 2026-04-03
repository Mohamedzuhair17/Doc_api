import { create } from "zustand";

interface AnalysisResult {
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

interface UploadedFile {
  file: File;
  progress: number;
  status: "idle" | "uploading" | "uploaded" | "error";
  error?: string;
}

interface UIState {
  currentFile: UploadedFile | null;
  analysisResult: AnalysisResult | null;
  activeTab: string;
  setCurrentFile: (file: UploadedFile | null) => void;
  setAnalysisResult: (result: AnalysisResult | null) => void;
  setActiveTab: (tab: string) => void;
  updateFileProgress: (progress: number) => void;
  setFileStatus: (status: UploadedFile["status"], error?: string) => void;
  reset: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  currentFile: null,
  analysisResult: null,
  activeTab: "text",
  setCurrentFile: (file) => set({ currentFile: file }),
  setAnalysisResult: (result) => set({ analysisResult: result }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  updateFileProgress: (progress) =>
    set((s) => ({
      currentFile: s.currentFile ? { ...s.currentFile, progress } : null,
    })),
  setFileStatus: (status, error) =>
    set((s) => ({
      currentFile: s.currentFile ? { ...s.currentFile, status, error } : null,
    })),
  reset: () => set({ currentFile: null, analysisResult: null, activeTab: "text" }),
}));
