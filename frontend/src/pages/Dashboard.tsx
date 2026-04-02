import { useRef } from "react";
import { useUIStore } from "@/store/uiStore";
import { usePolling } from "@/hooks/usePolling";
import HeroSection from "@/components/HeroSection";
import FileUploader from "@/components/FileUploader";
import ProgressPanel from "@/components/ProgressPanel";
import ResultCard from "@/components/ResultCard";

const Dashboard = () => {
  const uploadRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const activeTaskId = useUIStore((s) => s.activeTaskId);
  const { data } = usePolling(activeTaskId);
  const hasResults = data?.status === "completed";

  const scrollTo = (ref: React.RefObject<HTMLDivElement | null>) => {
    ref.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-background relative bg-grid-pattern">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-background/60 border-b border-border/50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundImage: "var(--gradient-neon)" }}>
              <svg className="w-4 h-4 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            </div>
            <span className="font-bold text-foreground">DocAI</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <button onClick={() => scrollTo(uploadRef)} className="text-muted-foreground hover:text-foreground transition">Upload</button>
            {activeTaskId && (
              <button onClick={() => scrollTo(resultsRef)} className="text-muted-foreground hover:text-foreground transition">Results</button>
            )}
          </div>
        </div>
      </nav>

      <HeroSection
        onUploadClick={() => scrollTo(uploadRef)}
        onViewResults={() => scrollTo(resultsRef)}
        hasResults={hasResults}
      />

      <div ref={uploadRef}>
        <FileUploader />
      </div>

      <ProgressPanel />

      <div ref={resultsRef}>
        <ResultCard />
      </div>

      {/* Footer */}
      <footer className="py-8 border-t border-border/50 text-center text-sm text-muted-foreground">
        <p>© 2026 DocAI · AI Document Intelligence Platform</p>
      </footer>
    </div>
  );
};

export default Dashboard;
