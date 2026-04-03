import { useState } from "react";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import json from "react-syntax-highlighter/dist/esm/languages/hljs/json";
import { atomOneDark } from "react-syntax-highlighter/dist/esm/styles/hljs";
import { useUIStore } from "@/store/uiStore";
import { toast } from "sonner";

SyntaxHighlighter.registerLanguage("json", json);

const tabs = [
  { id: "text", label: "Summary" },
  { id: "json", label: "Entities" },
  { id: "analysis", label: "Sentiment" },
];

const ResultCard = () => {
  const data = useUIStore((s) => s.analysisResult);
  const [activeTab, setActiveTab] = useState("text");

  if (!data || data.status !== "success") return null;

  const { summary, entities, sentiment } = data;
  const jsonStr = JSON.stringify(entities, null, 2);

  const copy = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  const download = () => {
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "extraction-result.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section id="results" className="py-16 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="glass-panel overflow-hidden neon-glow-violet">
          <div className="flex items-center border-b border-border">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-6 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {tab.label}
                {activeTab === tab.id && (
                  <span
                    className="absolute bottom-0 left-0 right-0 h-0.5"
                    style={{ backgroundImage: "var(--gradient-neon)" }}
                  />
                )}
              </button>
            ))}
          </div>

          <div className="p-6">
            {activeTab === "text" && (
              <div className="space-y-4">
                <div className="flex justify-end">
                  <button
                    onClick={() => copy(summary)}
                    className="text-xs text-muted-foreground hover:text-foreground transition flex items-center gap-1"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                    Copy
                  </button>
                </div>
                <div className="p-4 rounded-lg bg-muted/50 font-mono text-sm text-foreground whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto">
                  {summary}
                </div>
              </div>
            )}

            {activeTab === "json" && (
              <div className="space-y-4">
                <div className="flex justify-end gap-3">
                  <button
                    onClick={() => copy(jsonStr)}
                    className="text-xs text-muted-foreground hover:text-foreground transition flex items-center gap-1"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                    Copy
                  </button>
                  <button
                    onClick={download}
                    className="text-xs text-muted-foreground hover:text-foreground transition flex items-center gap-1"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                    Download
                  </button>
                </div>
                <div className="rounded-lg overflow-hidden max-h-96 overflow-y-auto">
                  <SyntaxHighlighter language="json" style={atomOneDark} customStyle={{ background: "hsl(260 25% 8%)", padding: "1rem", borderRadius: "0.5rem", fontSize: "0.85rem" }}>
                    {jsonStr}
                  </SyntaxHighlighter>
                </div>
              </div>
            )}

            {activeTab === "analysis" && (
              <div className="space-y-4">
                <div className="flex justify-end">
                  <button
                    onClick={() => copy(sentiment)}
                    className="text-xs text-muted-foreground hover:text-foreground transition flex items-center gap-1"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                    Copy
                  </button>
                </div>
                <div className="p-4 rounded-lg bg-muted/50 text-sm text-foreground whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto">
                  {sentiment}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default ResultCard;
