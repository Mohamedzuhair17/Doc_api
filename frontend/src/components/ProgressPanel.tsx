import { useUIStore } from "@/store/uiStore";

const ProgressPanel = () => {
  const currentFile = useUIStore((s) => s.currentFile);
  const analysisResult = useUIStore((s) => s.analysisResult);

  if (!currentFile) return null;

  const isUploading = currentFile.status === "uploading";
  const isCompleted = currentFile.status === "uploaded" && !!analysisResult;
  const isFailed = currentFile.status === "error";

  return (
    <section id="progress" className="py-16 px-6">
      <div className="max-w-2xl mx-auto">
        <div className="glass-panel p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-foreground">Processing Status</h3>
            <span className="text-xs text-muted-foreground">{currentFile.file.name}</span>
          </div>

          <div className="space-y-4">
            {isUploading && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-neon-cyan/10 text-neon-cyan">
                    <span className="w-2 h-2 rounded-full bg-current animate-pulse-glow" />
                    Uploading & Analyzing
                  </span>
                </div>
                <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{ width: `${currentFile.progress}%`, backgroundImage: "var(--gradient-neon)" }}
                  />
                </div>
                <p className="text-xs text-muted-foreground">{currentFile.progress}%</p>
              </>
            )}

            {isCompleted && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Status</span>
                <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-neon-cyan/10 text-neon-cyan">
                  Completed
                </span>
              </div>
            )}

            {isFailed && (
              <div className="mt-4 p-4 rounded-lg bg-destructive/5 border border-destructive/20">
                <p className="text-sm text-destructive">{currentFile.error || "Upload failed"}</p>
                <p className="text-xs text-muted-foreground mt-1">Please try uploading again.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProgressPanel;
