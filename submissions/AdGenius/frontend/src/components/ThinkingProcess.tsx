import React, { useState, useEffect } from "react";
import { SSEToolCall } from "../types";
import { Loader, BrainCircuit, ChevronDown, ChevronRight } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface ThinkingProcessProps {
  eventType: string | null;
  reasoning: string | null;
  tools: SSEToolCall[];
  isComplete: boolean;
  compact?: boolean;
  isForceExpand?: boolean;
}

/**
 * ThinkingProcess component displays AI reasoning and tool calls
 * Shows the thought process with expandable/collapsible behavior
 */
const ThinkingProcess: React.FC<ThinkingProcessProps> = ({
  eventType,
  reasoning,
  tools,
  isComplete,
  compact = false,
  isForceExpand = false,
}) => {
  // Initialize hooks first (before any conditional returns)
  const [isExpanded, setIsExpanded] = useState(!isComplete);

  // Update isExpanded when component becomes visible or is complete
  useEffect(() => {
    if (isForceExpand) {
      setIsExpanded(true);
    } else {
      setIsExpanded(!isComplete);
    }
  }, [isComplete, isForceExpand]);
  
  // Return null if there's nothing to display
  if (!eventType && !reasoning && (!tools || !Array.isArray(tools) || tools.length === 0)) {
    return null;
  }

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div
      className={`${compact ? "border-0 bg-transparent" : "border border-gray-200 bg-gray-50 rounded-lg mb-4 shadow-sm"} overflow-hidden transition-all duration-200 animate-fadeIn`}
    >
      <div
        className={`flex items-center cursor-pointer ${compact ? "px-0 py-1" : "px-3 py-2 bg-gray-100 border-b border-gray-200"}`}
        onClick={toggleExpand}
      >
        <div
          className={`flex items-center font-medium ${compact ? "text-gray-700" : "text-primary-700"}`}
        >
          {!isComplete && (
            <Loader className="h-3 w-3 mr-2 animate-spin text-primary-600" />
          )}
          {!compact && <BrainCircuit size={16} className="mr-2" />}
          {!compact && <span>AI Thinking Process</span>}
        </div>
        {isComplete && !compact ? (
          <span className="ml-2 text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-3 w-3 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            Process Complete
          </span>
        ) : !compact && eventType ? (
          <span className="ml-2 text-xs px-2 py-0.5 bg-gray-200 text-gray-700 rounded-full">
            {eventType}
          </span>
        ) : null}
        <div className="ml-auto">
          {isExpanded ? (
            <ChevronDown size={16} className="text-gray-500" />
          ) : (
            <ChevronRight size={16} className="text-gray-500" />
          )}
        </div>
      </div>

      <div
        className={`${isExpanded ? (compact ? "max-h-[300px] pt-2 pb-1" : "max-h-[500px] p-3") : "max-h-0 p-0 overflow-hidden"} transition-all duration-300 overflow-y-auto`}
      >
        {reasoning && typeof reasoning === 'string' && reasoning.trim() !== "" && (
          <div
            className={`border-l-2 border-primary-200 pl-3 mb-3 text-gray-700 ${compact ? "text-xs" : "text-sm"}`}
          >
            <ReactMarkdown>{reasoning}</ReactMarkdown>
          </div>
        )}

        {tools && Array.isArray(tools) && tools.length > 0 && (
          <div className="flex flex-col space-y-2">
            {tools
              .filter((tool) => !!tool && typeof tool === 'object')
              .map((tool) => (
                <ToolCallDisplay 
                  key={tool.tool_call_id}
                  tool={tool}
                  compact={compact}
                />
              ))}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * ToolCallDisplay component renders a single tool call with its arguments and results
 */
interface ToolCallDisplayProps {
  tool: SSEToolCall;
  compact?: boolean;
}

const ToolCallDisplay: React.FC<ToolCallDisplayProps> = ({ tool, compact = false }) => {
  return (
    <div
      className={`${compact ? "border-0 border-l border-gray-300" : "border rounded-md"} overflow-hidden`}
    >
      <div
        className={`flex items-center justify-between ${compact ? "bg-transparent py-1 px-2" : "bg-gray-100 p-2 border-b"}`}
      >
        <span
          className={`font-semibold text-xs ${compact ? "text-gray-600" : "text-primary-700"}`}
        >
          {tool.tool_name || 'Unknown Tool'}
        </span>
        {tool.metrics && typeof tool.metrics === 'object' && typeof tool.metrics.time === 'number' && (
          <span className="text-xs text-gray-500">
            {tool.metrics.time.toFixed(4)}s
          </span>
        )}
      </div>

      {tool.tool_args && Object.keys(tool.tool_args).length > 0 && (
        <div
          className={`${compact ? "bg-transparent px-2 py-1" : "bg-gray-50 p-3"} border-b`}
        >
          <div className="text-xs font-medium text-gray-600 mb-1">
            Arguments:
          </div>
          <pre
            className={`text-xs ${compact ? "bg-transparent p-0" : "bg-gray-100 p-2 rounded"} overflow-x-auto whitespace-pre-wrap text-gray-800`}
          >
            {JSON.stringify(tool.tool_args, null, 2)}
          </pre>
        </div>
      )}

      {tool.content && typeof tool.content === 'string' && (
        <div className={`${compact ? "px-2 py-1" : "p-3"}`}>
          <div className="text-xs font-medium text-gray-600 mb-1">
            Result:
          </div>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{tool.content}</ReactMarkdown>
          </div>
        </div>
      )}

      {!!tool.tool_call_error && (
        <div className="bg-red-50 text-red-600 p-2 text-xs">
          Error during tool execution
        </div>
      )}
    </div>
  );
};

// Export the ThinkingProcess component
export default ThinkingProcess;
