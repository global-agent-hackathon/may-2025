// src/components/UrlInput.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Link2, Loader2 } from "lucide-react"; // Changed icon
// Card import is not strictly needed if we don't wrap it in a card anymore, or use a simple div
// For consistency with Exa, the input is directly on the page, not in a card.

interface UrlInputProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
}

export const UrlInput = ({ onAnalyze, isLoading }: UrlInputProps) => {
  const [url, setUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onAnalyze(url.trim());
    }
  };

  return (
    // No Card wrapper needed to match Exa's simple input field style
    <div className="mb-10 md:mb-12">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="relative">
          {/* Icon can be removed if going for extreme simplicity like Exa's username input */}
          {/* <Link2 className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" /> */}
          <Input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter Your Portfolio URL"
            className="h-12 md:h-14 text-md 
                       bg-white border-slate-300 
                       text-slate-700 placeholder:text-slate-400 
                       focus:border-blue-500 focus:ring-1 focus:ring-blue-500
                       transition-colors rounded-md w-full px-4" // Simplified styling
            required
            disabled={isLoading}
          />
        </div>
        <Button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="w-full h-12 md:h-14 text-md font-medium 
                     bg-blue-600 hover:bg-blue-700 
                     text-white
                     rounded-md
                     transition-colors
                     disabled:opacity-60 disabled:bg-slate-400" // Simplified button
        >
          {isLoading ? (
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Analyzing...</span>
            </div>
          ) : (
            <span>Roast It!</span>
          )}
        </Button>
      </form>
    </div>
  );
};