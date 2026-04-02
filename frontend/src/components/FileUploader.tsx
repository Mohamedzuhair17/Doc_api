import { useCallback, useState } from "react";
import { useUpload } from "@/hooks/useUpload";
import { useUIStore } from "@/store/uiStore";

const ACCEPTED = ["application/pdf", "image/png", "image/tiff"];

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

const FileUploader = () => {
  const [isDragging, setIsDragging] = useState(false);
  const { upload, isUploading, retry, cancel } = useUpload();
  const [preview, setPreview] = useState<{ name: string; size: string } | null>(null);
  const currentFile = useUIStore((s) => s.currentFile);

  const handleFile = useCallback(
    (file: File) => {
      if (!ACCEPTED.includes(file.type)) return;
      setPreview({ name: file.name, size: formatSize(file.size) });
      upload(file);
    },
    [upload]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <section id="upload" className="py-16 px-6">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-8 text-foreground">Upload Your Document</h2>

        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
          className={`relative glass-panel p-12 text-center cursor-pointer transition-all duration-200 ${
            isDragging ? "neon-border" : "border-border hover:border-primary/30"
          } ${isUploading ? "pointer-events-none" : ""}`}
        >
          <input
            type="file"
            accept=".pdf,.png,.tiff,.tif"
            onChange={onSelect}
            className="absolute inset-0 opacity-0 cursor-pointer"
            disabled={isUploading}
          />

          {isUploading && currentFile ? (
            <div className="space-y-4">
              <div className="w-12 h-12 mx-auto border-2 border-primary border-t-transparent rounded-full animate-spin" />
              <p className="text-foreground font-medium">{preview?.name}</p>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{ width: `${currentFile.progress}%`, backgroundImage: "var(--gradient-neon)" }}
                />
              </div>
              <p className="text-sm text-muted-foreground">{currentFile.progress}%</p>
              <button onClick={(e) => { e.stopPropagation(); cancel(); }} className="text-sm text-destructive hover:underline">Cancel</button>
            </div>
          ) : currentFile?.status === "error" ? (
            <div className="space-y-4">
              <div className="w-12 h-12 mx-auto rounded-full bg-destructive/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </div>
              <p className="text-destructive font-medium">Upload Failed</p>
              <p className="text-sm text-muted-foreground">{currentFile.error}</p>
              <button onClick={(e) => { e.stopPropagation(); retry(); }} className="px-4 py-2 rounded-lg text-sm font-medium border border-primary/40 text-primary hover:bg-primary/10 transition">Retry Upload</button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center neon-glow-violet">
                <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
              </div>
              <div>
                <p className="text-foreground font-medium">{isDragging ? "Drop your file here" : "Drag & drop your document"}</p>
                <p className="text-sm text-muted-foreground mt-1">or click to browse · PDF, PNG, TIFF</p>
              </div>
            </div>
          )}
        </div>

        {preview && currentFile?.status === "uploaded" && (
          <div className="mt-4 glass-panel p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">{preview.name}</p>
                <p className="text-xs text-muted-foreground">{preview.size}</p>
              </div>
            </div>
            <span className="text-xs text-neon-cyan font-medium">✓ Uploaded</span>
          </div>
        )}
      </div>
    </section>
  );
};

export default FileUploader;
