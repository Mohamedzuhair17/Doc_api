interface HeroSectionProps {
  onUploadClick: () => void;
  onViewResults: () => void;
  hasResults: boolean;
}

const HeroSection = ({ onUploadClick, onViewResults, hasResults }: HeroSectionProps) => {
  return (
    <section className="relative py-20 md:py-32 text-center">
      {/* Gradient orbs */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-primary/10 blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 left-1/4 w-[300px] h-[300px] rounded-full bg-neon-cyan/5 blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto px-6">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 rounded-full border border-primary/30 bg-primary/5 text-sm text-primary opacity-100">
          <span className="w-2 h-2 rounded-full bg-neon-cyan animate-pulse-glow" />
          AI-Powered Document Intelligence
        </div>

        <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold leading-tight tracking-tight mb-6">
          <span className="gradient-text">AI Document</span>
          <br />
          <span className="text-foreground">Intelligence Platform</span>
        </h1>

        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload documents and extract structured insights instantly using
          AI-powered document processing.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={onUploadClick}
            className="px-8 py-3.5 rounded-lg font-semibold text-primary-foreground neon-glow-violet transition-all duration-300"
            style={{ backgroundImage: "var(--gradient-neon)", backgroundSize: "200% 200%" }}
          >
            Upload Document
          </button>

          {hasResults && (
            <button
              onClick={onViewResults}
              className="px-8 py-3.5 rounded-lg font-semibold border border-primary/40 text-foreground hover:bg-primary/10 transition-all duration-300"
            >
              View Results
            </button>
          )}
        </div>
      </div>

    </section>
  );
};

export default HeroSection;
