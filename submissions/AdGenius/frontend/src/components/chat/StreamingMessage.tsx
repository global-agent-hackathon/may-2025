import React from "react";
import { Loader, BrainCircuit } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface StreamingMessageProps {
  content: string;
  showThinking: boolean;
  toggleThinkingDisplay: () => void;
  streamingState: {
    reasoning: string | null;
  };
}

const StreamingMessage: React.FC<StreamingMessageProps> = ({
  content,
  showThinking,
  toggleThinkingDisplay,
  streamingState,
}) => {
  return (
    <div className="flex justify-start mb-6">
      <div className="bg-white p-4 rounded-2xl rounded-bl-sm shadow-soft">
        <div className="text-[15px] leading-relaxed">
          <ReactMarkdown className="prose prose-sm max-w-none leading-normal [&_p]:my-1 [&_ul]:my-1 [&_ol]:my-1 [&_li]:my-0.5 [&_h1]:mt-3 [&_h1]:mb-2 [&_h2]:mt-2 [&_h2]:mb-1 [&_h3]:mt-2 [&_h3]:mb-1 [&_blockquote]:my-1">
            {content}
          </ReactMarkdown>
        </div>
        <div className="flex items-center justify-between text-xs mt-2 text-gray-400">
          <div className="flex items-center">
            <Loader className="h-3 w-3 mr-1 animate-spin" />
            <span>Typing...</span>
          </div>
          <button
            onClick={() => {
              toggleThinkingDisplay();
              if (streamingState.reasoning) {
                document
                  .getElementById("thinking-process-panel")
                  ?.scrollIntoView({ behavior: "smooth" });
              }
            }}
            className="flex items-center bg-primary-50 border border-primary-100 px-2 py-1 rounded-full text-primary-600 hover:bg-primary-100 transition-colors"
            title={showThinking ? "Hide AI process" : "Show AI process"}
          >
            <BrainCircuit size={14} className="mr-1" />
            <span>{showThinking ? "Hide process" : "Show process"}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default StreamingMessage;