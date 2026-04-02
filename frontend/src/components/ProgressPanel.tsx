import { usePolling } from "@/hooks/usePolling";
import { useUIStore } from "@/store/uiStore";

const statusConfig = {
  queued: { label: "Queued", color: "text-muted-foreground", bg: "bg-muted", glow: "" },
  processing: { label: "Processing", color: "text-neon-cyan", bg: "bg-neon-cyan/10", glow: "neon-glow-cyan" },
  completed: { label: "Completed", color: "text-neon-cyan", bg: "bg-neon-cyan/10", glow: "neon-glow-cyan" },
  failed: { label: "Failed", color: "text-destructive", bg: "bg-destructive/10", glow: "" },
};

const ProgressPanel = () => {
  const activeTaskId = useUIStore((s) => s.activeTaskId);
  const { data, isLoading, refetch } = usePolling(activeTaskId);

  if (!activeTaskId) return null;

  const status = data?.status || "queued";
  const config = statusConfig[status];

  return (
    <section id="progress" className="py-16 px-6">
      <div className="max-w-2xl mx-auto">
        <div className={`glass-panel p-8 ${config?.glow || ""}`}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-foreground">Processing Status</h3>
            <button
              onClick={() => refetch()}
              className="text-sm text-muted-foreground hover:text-foreground transition"
            >
              ↻ Refresh
            </button>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Task ID</span>
              <span className="text-sm font-mono text-foreground">{activeTaskId.slice(0, 12)}...</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Status</span>
              <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${config?.bg || ""} ${config?.color || ""}`}>
                {(status === "processing" || (status === "queued" && !isLoading)) && (
                  <span className="w-2 h-2 rounded-full bg-current animate-pulse-glow" />
                )}
                {config?.label || "Queued"}
              </span>
            </div>

            {(status === "queued" || status === "processing") && (
              <div className="mt-4">
                <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: status === "queued" ? "20%" : "70%", backgroundImage: "var(--gradient-neon)" }}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {status === "queued" ? "Waiting in queue..." : "AI is analyzing your document..."}
                </p>
              </div>
            )}

            {status === "failed" && data?.error && (
              <div className="mt-4 p-4 rounded-lg bg-destructive/5 border border-destructive/20">
                <p className="text-sm text-destructive">{data.error}</p>
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
