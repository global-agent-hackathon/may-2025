import React from "react";
import ThinkingProcess from "../ThinkingProcess";
import { SSEToolCall } from "../../types/index";

interface ThinkingProcessDisplayProps {
  streamingState: {
    currentEventType: string | null;
    reasoning: string | null;
    tools: SSEToolCall[];
    isDone: boolean;
  };
  toggleThinkingDisplay?: () => void;
}

const ThinkingProcessDisplay: React.FC<ThinkingProcessDisplayProps> = ({
  streamingState,
}) => {
  return (
    <div className="mb-4 animate-fadeIn" id="thinking-process-panel">
      <ThinkingProcess
        eventType={streamingState.currentEventType || "Thinking"}
        reasoning={streamingState.reasoning}
        tools={streamingState.tools || []}
        isComplete={streamingState.isDone}
        compact={false}
      />
    </div>
  );
};

export default ThinkingProcessDisplay;