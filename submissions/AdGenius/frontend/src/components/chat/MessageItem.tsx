import React from "react";
import { ChatMessage, SSEToolCall } from "../../types/index";
import UserMessageItem from "./UserMessageItem";
import AIMessageItem from "./AIMessageItem";

interface MessageItemProps {
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

const MessageItem: React.FC<MessageItemProps> = ({
  message,
  isLastMessage,
  activeThinkingMessageId,
  streamingState,
  showThinking,
  isStreaming,
  setActiveThinkingMessageId,
  toggleThinkingDisplay,
}) => {
  const isUser = message.sender === "user";

  return (
    <div
      id={`message-${message.id}`}
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-6`}
    >
      {isUser ? (
        <UserMessageItem message={message} />
      ) : (
        <AIMessageItem
          message={message}
          isLastMessage={isLastMessage}
          activeThinkingMessageId={activeThinkingMessageId}
          streamingState={streamingState}
          showThinking={showThinking}
          isStreaming={isStreaming}
          setActiveThinkingMessageId={setActiveThinkingMessageId}
          toggleThinkingDisplay={toggleThinkingDisplay}
        />
      )}
    </div>
  );
};

export default MessageItem;
