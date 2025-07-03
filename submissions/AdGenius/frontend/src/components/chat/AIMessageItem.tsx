import React from "react";
import { BrainCircuit, ChevronDown, ChevronRight } from "lucide-react";
import { ChatMessage, SSEToolCall } from "../../types/index";
import ThinkingProcess from "../ThinkingProcess";
import ReactMarkdown from "react-markdown";

interface AIMessageItemProps {
  message: ChatMessage;
  isLastMessage: boolean;
  activeThinkingMessageId: string | null;
  streamingState: {
    currentEventType: string | null;
    reasoning: string | null;
    tools: SSEToolCall[];
    isDone: boolean;
    content?: string;
  };
  showThinking: boolean;
  isStreaming: boolean;
  setActiveThinkingMessageId: (id: string | null) => void;
  toggleThinkingDisplay: () => void;
}

const AIMessageItem: React.FC<AIMessageItemProps> = ({
  message,
  isLastMessage,
  activeThinkingMessageId,
  streamingState,
  showThinking,
  isStreaming,
  setActiveThinkingMessageId,
  toggleThinkingDisplay,
}) => {
  // Check if this message has thinking process data
  const hasThinkingProcess =
    (message.thinkingProcess && message.thinkingProcess.reasoning) ||
    (isLastMessage && streamingState?.reasoning);

  // Check if this message is the one with active thinking display
  const isActiveThinkingMessage = message.id === activeThinkingMessageId;

  // Determine if thinking process details should be shown
  const shouldShowThinkingDetails =
    isActiveThinkingMessage ||
    (isLastMessage && showThinking && (isStreaming || streamingState?.isDone));

  const scrollToMessage = () => {
    setTimeout(() => {
      const messageElement = document.getElementById(`message-${message.id}`);
      if (messageElement) {
        messageElement.scrollIntoView({ behavior: "smooth" });
      }
    }, 100);
  };

  // Handle clicking on the thinking process header
  const handleThinkingHeaderClick = () => {
    if (isLastMessage) {
      // For the last message, toggle the global thinking display
      toggleThinkingDisplay();
    } else {
      // For previous messages, toggle this specific message's thinking display
      setActiveThinkingMessageId(isActiveThinkingMessage ? null : message.id);
    }
  };

  return (
    <div className="max-w-[85%] p-4 rounded-2xl shadow-sm bg-white text-gray-800 rounded-bl-sm">
      <div className="text-[15px]">
        <ReactMarkdown className="prose prose-sm max-w-none leading-normal [&_p]:my-1 [&_ul]:my-1 [&_ol]:my-1 [&_li]:my-0.5 [&_h1]:mt-3 [&_h1]:mb-2 [&_h2]:mt-2 [&_h2]:mb-1 [&_h3]:mt-2 [&_h3]:mb-1 [&_blockquote]:my-1">
          {message.content}
        </ReactMarkdown>
      </div>
      {message.image && (
        <img
          src={message.image}
          alt="Ad creative"
          className="mt-3 rounded-xl w-full h-auto max-h-64 object-cover"
        />
      )}

      {/* Show thinking process header for all AI messages that have thinking data */}
      {hasThinkingProcess && (
        <div className="mt-3 border-t border-gray-100 pt-3">
          <div
            className="flex items-center justify-between cursor-pointer mb-2"
            onClick={handleThinkingHeaderClick}
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center text-primary-600">
                <BrainCircuit size={14} className="mr-1" />
                <span className="text-sm font-medium">
                  AI Thinking Process
                </span>
              </div>
              {shouldShowThinkingDetails ? (
                <ChevronDown size={16} className="text-gray-400" />
              ) : (
                <ChevronRight size={16} className="text-gray-400" />
              )}
            </div>
          </div>

          {/* Show thinking process details based on determined condition */}
          {shouldShowThinkingDetails && (
            <ThinkingProcess
              eventType={
                isLastMessage
                  ? streamingState?.currentEventType
                  : message.thinkingProcess?.eventType || null
              }
              reasoning={
                isLastMessage
                  ? streamingState?.reasoning
                  : message.thinkingProcess?.reasoning || null
              }
              tools={
                isLastMessage
                  ? streamingState?.tools || []
                  : message.thinkingProcess?.tools || []
              }
              isComplete={
                isLastMessage
                  ? streamingState?.isDone
                  : message.thinkingProcess?.isComplete || false
              }
              compact={true}
              isForceExpand={true}
            />
          )}
        </div>
      )}

      <div className="flex items-center justify-between text-xs mt-2 text-gray-400">
        <div>
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
        {hasThinkingProcess && (
          <button
            onClick={() => {
              // Toggle thinking display for this message
              if (isLastMessage) {
                toggleThinkingDisplay();
              } else {
                if (isActiveThinkingMessage) {
                  setActiveThinkingMessageId(null);
                } else {
                  setActiveThinkingMessageId(message.id);
                  scrollToMessage();
                }
              }
            }}
            className={`flex items-center ml-2 ${
              shouldShowThinkingDetails
                ? "bg-blue-100 text-blue-600 hover:bg-blue-200"
                : "bg-blue-50 text-blue-600 hover:bg-blue-100"
            } px-2 py-0.5 rounded-full text-xs transition-colors`}
            title={
              shouldShowThinkingDetails
                ? "Hide AI thinking process"
                : "View AI thinking process"
            }
          >
            <BrainCircuit size={12} className="mr-1" />
            <span>
              {shouldShowThinkingDetails ? "Hide process" : "View process"}
            </span>
          </button>
        )}
      </div>
    </div>
  );
};

export default AIMessageItem;