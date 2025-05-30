// src/pages/Index.tsx
import { useState } from "react";
import { Header } from "@/components/Header";
import { UrlInput } from "@/components/UrlInput";
// AnalysisResult type will be updated because it's imported from ResultsCard
import { ResultsCard, AnalysisResult } from "@/components/ResultsCard"; 
import { FirecrawlService } from "@/utils/firecrawlService";
import { GeminiService } from "@/utils/geminiService";
import { useToast } from "@/hooks/use-toast"; 

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [analyzedUrl, setAnalyzedUrl] = useState<string>("");
  const { toast } = useToast();

  const handleAnalyze = async (url: string) => {
    setIsLoading(true);
    setResult(null);
    setAnalyzedUrl(url);

    try {
      toast({
        title: "🕷️ Crawling your portfolio...",
        description: "Accessing the digital archives...",
      });

      const scrapeResult = await FirecrawlService.scrapePortfolio(url);
      if (!scrapeResult.success || !scrapeResult.content) {
        throw new Error(scrapeResult.error || 'Failed to scrape portfolio content.');
      }
      toast({
        title: "🤖 AI Processing...",
        description: "Extracting insights and preparing your roast.",
      });
      const analysisResult = await GeminiService.analyzePortfolio(scrapeResult.content, url);
      if (!analysisResult.success || !analysisResult.result) {
        throw new Error(analysisResult.error || 'AI analysis failed to produce results.');
      }
      setResult(analysisResult.result);
      toast({
        title: "✨ Analysis Complete!",
        description: "Your portfolio roast is ready.",
        duration: 5000,
      });
    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "⚠️ Error",
        description: error instanceof Error ? error.message : "An unknown error occurred.",
        variant: "destructive",
      });
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // Apply the grid pattern and overall light theme styling
    <div className="min-h-screen bg-background text-foreground 
                   bg-grid-pattern bg-grid-pattern-size 
                   selection:bg-blue-500 selection:text-white">
      <div className="container mx-auto px-4 py-12 md:py-20">
        <Header />
        
        <div className="max-w-2xl mx-auto"> {/* Max width for input section */}
          <UrlInput onAnalyze={handleAnalyze} isLoading={isLoading} />
          
          {result && (
            <div className="mt-12 md:mt-16">
              <ResultsCard result={result} originalUrl={analyzedUrl} />
            </div>
          )}
        </div>

        <footer className="text-center mt-24 text-slate-500 text-sm">
          <br></br><br></br>
          <p>Built for May 2025 Global Agent Hackathon 🚀</p>
          <p className="mt-1">
            Powered by Firecrawl + Gemini AI • Made by Chirag
          </p>
           {/* Optional: Link to your own Twitter or project page like Exa */}
          <a 
            href="https://x.com/Chiragjoshi_12" // Replace
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block bg-slate-800 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-700 transition-colors"
          >
            Follow us on X for more tools
          </a>
        </footer>
      </div>
    </div>
  );
};

export default Index;
