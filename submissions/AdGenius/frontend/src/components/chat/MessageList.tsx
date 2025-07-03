import React, { useRef, useEffect } from "react";
import { Loader } from "lucide-react";
import { ChatMessage, ConnectionStatus, SSEToolCall } from "../../types/index";
import MessageItem from "./MessageItem";
import StreamingMessage from "./StreamingMessage";
import ThinkingProcessDisplay from "./ThinkingProcessDisplay";

interface MessageListProps {
  messages: ChatMessage[];
  streamingState: {
    currentEventType: string | null;
    reasoning: string | null;
    tools: SSEToolCall[];
    isDone: boolean;
    content?: string;
  };
  isLoading: boolean;
  isStreaming: boolean;
  streamingContent: string;
  error: string | null;
  connectionStatus?: ConnectionStatus;
  showThinking: boolean;
  activeThinkingMessageId: string | null;
  setActiveThinkingMessageId: (id: string | null) => void;
  toggleThinkingDisplay: () => void;
  setError: (error: string | null) => void;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  streamingState,
  isLoading,
  isStreaming,
  streamingContent,
  error,
  connectionStatus,
  showThinking,
  activeThinkingMessageId,
  setActiveThinkingMessageId,
  toggleThinkingDisplay,
  setError,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Debug messages received
  useEffect(() => {
    console.log('MessageList received messages:', messages);
  }, [messages]);

  // Scroll to bottom when messages change or streaming content updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  return (
    <div 
      className="h-full overflow-y-auto p-4 md:p-6 space-y-4 message-list-scrollbar"
      style={{
        // Firefox scrollbar styles
        scrollbarWidth: 'thin' as const,
        scrollbarColor: '#3a72ff #f1f1f1',
      }}
    >
      {/* No messages state */}
      {messages.length === 0 && !isLoading && !isStreaming && (
        <div className="text-center py-10">
          <div className="text-gray-500 mb-2">No messages to display. Start a conversation!</div>
        </div>
      )}

      {messages.filter((m) => m && m.content).map((message, index) => (
        <MessageItem
          key={message.id}
          message={message}
          isLastMessage={index === messages.length - 1}
          activeThinkingMessageId={activeThinkingMessageId}
          streamingState={streamingState}
          showThinking={showThinking}
          isStreaming={isStreaming}
          setActiveThinkingMessageId={setActiveThinkingMessageId}
          toggleThinkingDisplay={toggleThinkingDisplay}
        />
      ))}

      {/* Thinking Process Display for streaming messages */}
      {isStreaming && showThinking && streamingState && (
        <ThinkingProcessDisplay
          streamingState={streamingState}
          toggleThinkingDisplay={toggleThinkingDisplay}
        />
      )}

      {/* Streaming message */}
      {isStreaming && streamingContent && (
        <StreamingMessage
          content={streamingContent}
          showThinking={showThinking}
          toggleThinkingDisplay={toggleThinkingDisplay}
          streamingState={streamingState}
        />
      )}

      {/* Loading indicator */}
      {isLoading && !isStreaming && (
        <div className="flex justify-start mb-6">
          <div className="bg-white p-4 rounded-2xl rounded-bl-sm shadow-soft">
            <div className="flex items-center text-gray-500">
              <Loader className="h-5 w-5 mr-2 animate-spin" />
              <span className="text-[15px]">AdGenius is thinking...</span>
            </div>
          </div>
        </div>
      )}

      {/* Connection status */}
      {connectionStatus === 'reconnecting' && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 p-3 rounded-lg mb-4 flex items-center">
          <span>Reconnecting to server...</span>
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg mb-4 flex items-center">
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            ✕
          </button>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;