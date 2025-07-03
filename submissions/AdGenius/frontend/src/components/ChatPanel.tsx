import React, { useState, useEffect, useRef } from "react";
import { ChatMessage } from "../types";
import { chatService } from "../services/chatService";
import useSSEParser from "../hooks/useSSEParser";
import MessageList from "./chat/MessageList";
import InputArea from "./chat/InputArea";
import DetailsSidePanel from "./chat/DetailsSidePanel";
import WorkflowProgress from "./chat/WorkflowProgress";
import { WorkflowProvider } from "./chat/WorkflowContext";
import { useWorkflow } from "./chat/useWorkflow";
import { ChevronRight } from "lucide-react";

interface ChatPanelProps {
  conversationId?: string | null;
}

/**
 * Internal chat panel component that uses the workflow context
 */
const InnerChatPanel: React.FC<ChatPanelProps> = ({
  conversationId: initialConversationId,
}) => {
  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const PAGE_SIZE = 20;
  const [offset, setOffset] = useState(0);
  const [newMessage, setNewMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isDetailsPanelOpen, setIsDetailsPanelOpen] = useState(false);
  const [activeThinkingMessageId, setActiveThinkingMessageId] = useState<
    string | null
  >(null);

  // Access workflow context
  const {
    currentWorkflow,
    handlePublish: workflowHandlePublish,
    fetchDraftCampaigns,
  } = useWorkflow();

  // Helper method to handle stream errors consistently
  // Refactored: Only reset streaming state on fatal errors, not on connection errors
  const handleStreamError = (error: unknown, errorType: string, options?: { fatal?: boolean }) => {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    console.error(`${errorType}:`, error);
    setError(`${errorType}: ${errorMessage}`);
    setIsStreaming(false);
    setIsLoading(false);
    if (options?.fatal) {
      resetStreamingState();
    }
    closeConnection();
  };

  // SSE streaming state
  const {
    streamingState,
    connectionError,
    connectionStatus,
    startStreaming,
    handleSSEEvent,
    resetStreamingState,
    markStreamingComplete,
    createEventSourceConnection,
    closeConnection,
  } = useSSEParser();

  // UI state
  const [showThinking, setShowThinking] = useState(true);
  const [chatWidth, setChatWidth] = useState(0); // 0 means default flex
  const [isResizing, setIsResizing] = useState(false);
  const [isDesktop, setIsDesktop] = useState(false);
  const chatPanelRef = useRef<HTMLDivElement>(null);

  // API state
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId || null,
  );
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [error, setError] = useState<string | null>(null);

  // EventSource object reference for cleanup
  const eventSourceRef = useRef<EventSource | null>(null);

  // Update conversationId when initialConversationId changes
  useEffect(() => {
    if (initialConversationId) {
      console.log(
        "Setting conversationId state from prop:",
        initialConversationId,
      );
      // If it's coming from URL params, it might be in the format "xxxxx_conversation"
      // Let's extract just the conversation ID part
      let cleanId = initialConversationId;
      if (initialConversationId.includes("_conversation")) {
        cleanId = initialConversationId.split("_")[0];
        console.log("Extracted clean ID from URL format:", cleanId);
      }
      setConversationId(cleanId);
    }
  }, [initialConversationId]);

  // Load paginated messages when conversationId changes
  useEffect(() => {
    console.log("conversationId state changed:", conversationId);
    const loadInitialMessages = async () => {
      // Use the current conversationId rather than initialConversationId
      const idToUse = conversationId;
      if (!idToUse) {
        console.log("No conversation ID available, showing new chat interface");
        // Show welcome message for new conversations
        const welcomeMessage: ChatMessage = {
          id: "welcome-msg",
          content:
            "Hello! I'm AdGenius, your AI assistant for creating and optimizing ad campaigns. How can I help you today?",
          sender: "bot",
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMessage]);
        setHasMore(false);
        setOffset(0);
        setIsLoading(false);
        return;
      }
      console.log("Loading initial messages for conversation:", idToUse);
      setIsLoading(true);
      setIsLoadingHistory(true);
      setOffset(0);
      try {
        const data = await chatService.getConversationMessages(
          idToUse,
          PAGE_SIZE,
          0,
        );
        console.log("Received messages data:", data);
        // Map API response to UI message format
        const formattedMessages = chatService.mapApiMessagesToUIFormat(
          data.messages || [],
        );
        console.log("Formatted messages ready for display:", formattedMessages);

        // Add welcome message if there are no messages
        if (formattedMessages.length === 0) {
          console.log("No messages found, adding welcome message");
          formattedMessages.unshift({
            id: "welcome-msg",
            content:
              "Hello! I'm AdGenius, your AI assistant for creating and optimizing ad campaigns. How can I help you today?",
            sender: "bot",
            timestamp: new Date().toISOString(),
          });
        }

        setMessages(formattedMessages);
        console.log("Messages state updated:", formattedMessages);
        setHasMore((data.messages?.length || 0) === PAGE_SIZE);
        setOffset(data.messages?.length || 0);
      } catch (error) {
        console.error("Error loading messages:", error);
        setError("Failed to load messages");
      } finally {
        setIsLoading(false);
        setIsLoadingHistory(false);
      }
    };
    loadInitialMessages();
  }, [conversationId]);

  // Load more (older) messages
  const handleLoadMore = async () => {
    if (!conversationId || isLoadingHistory || !hasMore) return;
    console.log(
      "Loading more messages, offset:",
      offset,
      "conversation:",
      conversationId,
    );
    setIsLoadingHistory(true);
    try {
      const data = await chatService.getConversationMessages(
        conversationId,
        PAGE_SIZE,
        offset,
      );
      console.log("Loaded more messages data:", data);
      if (data.messages && data.messages.length > 0) {
        const formattedMessages = chatService.mapApiMessagesToUIFormat(
          data.messages,
        );
        console.log("Additional formatted messages:", formattedMessages);
        setMessages((prev) => [...formattedMessages, ...prev]);
        console.log("Updated messages array with new older messages");
        setOffset((prev) => prev + data.messages.length);
        setHasMore(data.messages.length === PAGE_SIZE);
      } else {
        console.log("No more messages available");
        setHasMore(false);
      }
    } catch (error) {
      console.error("Error loading more messages:", error);
      setError("Failed to load more messages");
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Clean up EventSource on unmount
  useEffect(() => {
    return () => {
      closeConnection();
    };
  }, [closeConnection]);

  // Watch for connection status and errors from our hook
  useEffect(() => {
    // Update error state based on connectionError
    if (connectionStatus === "connected" && connectionError) {
      // If connection is established but there's still an error message, clear it
      setError(null);
    } else if (connectionError) {
      // Otherwise show the connection error
      setError(connectionError);
    }
  }, [connectionError, connectionStatus]);

  // Check for desktop/mobile view
  useEffect(() => {
    const checkDesktop = () => setIsDesktop(window.innerWidth >= 1024);
    checkDesktop();
    window.addEventListener("resize", checkDesktop);
    return () => window.removeEventListener("resize", checkDesktop);
  }, []);

  // Mouse event handlers for resizing
  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      // Only allow resizing on lg screens and up
      if (window.innerWidth < 1024) return;

      const container = chatPanelRef.current?.parentElement;
      if (!container) return;

      const rect = container.getBoundingClientRect();
      let newWidth = e.clientX - rect.left;

      // Clamp min/max width
      const min = 320; // px
      const max = rect.width - 320; // px
      if (newWidth < min) newWidth = min;
      if (newWidth > max) newWidth = max;

      setChatWidth(newWidth);
    };

    const handleMouseUp = () => setIsResizing(false);

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing]);

  /**
   * Toggle thinking process display
   */
  const toggleThinkingDisplay = () => {
    setShowThinking(!showThinking);
  };

  /**
   * Toggle recording state
   */
  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  /**
   * Publish the campaign
   */
  const handlePublish = async () => {
    setIsDetailsPanelOpen(false);

    // Use the context's handlePublish function to update UI state
    await workflowHandlePublish();

    // Instead of adding a mock message, we'll set up the message content
    // and use the regular handleSendMessage flow
    setNewMessage("Please publish the campaign");
    
    // Use setTimeout to ensure state is updated before we call handleSendMessage
    setTimeout(() => {
      handleSendMessage();
    }, 50);
  };

  /**
   * Handles sending a new message
   */
  const handleSendMessage = async () => {
    if ((newMessage.trim() === "" && !isRecording) || isStreaming) return;

    // Generate a unique message ID for idempotency
    const messageId = chatService.generateMessageId();

    const userMessage: ChatMessage = {
      id: messageId, // Use the generated message ID
      content: newMessage,
      sender: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, userMessage]);
    setNewMessage("");
    setIsLoading(true);

    // Close any existing connection
    closeConnection();

    try {
      // Initialize streaming state
      setIsStreaming(true);
      setStreamingContent("");
      startStreaming(messageId);
      setIsLoading(false);
      setError(null);

      // Regular API flow
      const response = await chatService.sendMessage(
        userMessage.content,
        conversationId || undefined,
      );

      const newConversationId = response.conversation_id;

      // Update conversation ID if this is a new one
      if (!conversationId) {
        console.log("New conversation started, setting ID:", newConversationId);
        setConversationId(newConversationId);
      }

      // Use response.id as user_message_id and generate a new message_id for streaming
      const userMessageId = response.id;
      const streamingMessageId = chatService.generateMessageId();

      const streamUrl = chatService.prepareChatStreamUrl(
        newConversationId,
        userMessageId, // user_message_id from backend
        streamingMessageId, // new message_id for streaming/generation
      );

      // Log the message IDs for tracking and current conversation
      console.log(
        `Creating streaming connection for conversation ${newConversationId} with user_message_id: ${userMessageId} and message_id: ${streamingMessageId}`,
      );

      // Set up message handler
      const handleStreamMessage = (event: MessageEvent) => {
        try {
          // Use our custom hook to process the event
          const sseEvent = handleSSEEvent(event.data);
          if (!sseEvent) return;

          // Update the streaming content (for display in the UI)
          if (
            sseEvent.event_type === "RunResponse" &&
            sseEvent.data &&
            sseEvent.data.content
          ) {
            setStreamingContent((prev) => prev + sseEvent.data.content);
          }

          // When the stream is complete
          if (sseEvent.event_type === "RunCompleted" && sseEvent.done) {
            // When streaming is done, use either the full content from the completion event
            // or what we've accumulated so far in the streaming state
            const finalContent =
              sseEvent.data.content ||
              streamingContent ||
              streamingState.content;

            // Log completion with message ID for tracking
            console.log(
              `Stream completed for message_id: ${messageId}, streaming state message_id: ${streamingState.messageId}`,
            );

            // Refresh draft campaigns when streaming is complete
            if (conversationId) {
              fetchDraftCampaigns(conversationId);
            }

            // Only add message if there's actual content
            if (finalContent && finalContent.trim() !== "") {
              // Create a unique ID for this message
              const messageId = `assistant-${Date.now()}`;

              // Store thinking process data with the message
              const botMessage: ChatMessage = {
                id: messageId,
                content: finalContent,
                sender: "bot",
                timestamp: new Date().toISOString(),
                thinkingProcess: {
                  eventType: streamingState.currentEventType,
                  reasoning: streamingState.reasoning,
                  tools: streamingState.tools || [], // The hook ensures tools is always defined
                  isComplete: true,
                },
              };

              setMessages((prev) => [...prev, botMessage]);
              setStreamingContent("");
              setIsStreaming(false);
              setIsDetailsPanelOpen(true);
              setActiveThinkingMessageId(messageId);
              markStreamingComplete();
            } else {
              handleStreamError(
                new Error("No content available in the final message"),
                "Response error",
                { fatal: true }
              );
            }
          }

          if (
            sseEvent.event_type === "RunError" &&
            sseEvent.data &&
            typeof sseEvent.data === "object"
          ) {
            // Log the error_message to the console
            if ("error_message" in sseEvent.data) {
              console.error(sseEvent.data.error_message);
            }
            // Show the details as the error to the user
            handleStreamError(
              new Error(
                "details" in sseEvent.data
                  ? (sseEvent.data.details as string)
                  : "Unknown error"
              ),
              "Server error",
              { fatal: true }
            );
          }
        } catch (error) {
          handleStreamError(error, "Error processing SSE event", { fatal: true });
        }
      };

      // Create connection with our enhanced connection logic
      // Note: the connectionStatus is managed within the createEventSourceConnection method
      const eventSource = createEventSourceConnection(
        streamUrl,
        handleStreamMessage,
        // Add a callback function for when streaming completes
        () => {
          if (conversationId) {
            fetchDraftCampaigns(conversationId);
            console.log("Refreshing draft campaigns after stream completion");
          }
        }
      );
      eventSourceRef.current = eventSource;
    } catch (err) {
      handleStreamError(err, "Failed to send message", { fatal: true });
    }
  };

  /**
   * Sends a specified message to the AI Assistant
   */
  const sendSpecificMessage = (messageContent: string) => {
    // Set the message in the input field
    setNewMessage(messageContent);
    
    // Use setTimeout to ensure state is updated before we call handleSendMessage
    setTimeout(() => {
      handleSendMessage();
    }, 50);
  };

  return (
    <div className="h-full flex flex-col lg:flex-row" ref={chatPanelRef}>
      {/* Main Chat Area */}
      <div
        className="flex flex-col overflow-hidden bg-gray-50 border border-gray-200/50 h-full"
        style={{
          flex: chatWidth === 0 ? 1 : "none",
          width: chatWidth === 0 ? undefined : chatWidth,
          transition: isResizing ? "none" : "width 0.2s",
          maxHeight: "100vh",
        }}
      >
        {/* AI Chat Assistant Header - Sticky */}
        <div className="bg-white p-4 border-b border-gray-200 z-10 shadow-sm flex-shrink-0">
          <h2 className="font-semibold text-lg">AI Chat Assistant</h2>
        </div>
        
        {/* Process Status (Mobile) */}
        <div className="lg:hidden p-4 bg-white border-b border-gray-100 flex-shrink-0">
          <div className="mb-2">
            <WorkflowProgress steps={currentWorkflow} />
          </div>
          <button
            onClick={() => setIsDetailsPanelOpen(!isDetailsPanelOpen)}
            className="w-full mt-3 py-2 px-4 text-sm font-medium rounded-lg border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 flex items-center justify-center"
          >
            {isDetailsPanelOpen ? "Hide Details" : "Show Campaign Details"}
            <ChevronRight
              className={`ml-1 h-4 w-4 transition-transform ${isDetailsPanelOpen ? "rotate-90" : ""}`}
            />
          </button>
        </div>

        {/* Load More Button for history */}
        {hasMore && conversationId && (
          <button
            onClick={handleLoadMore}
            disabled={isLoadingHistory}
            className="mx-auto my-2 px-4 py-2 text-sm bg-white border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50 flex-shrink-0"
          >
            {isLoadingHistory ? "Loading..." : "Load More"}
          </button>
        )}

        {/* Chat content area - flex-grow and overflow-auto for scrolling */}
        <div className="flex-grow flex flex-col overflow-hidden h-full">
          <MessageList
            messages={messages}
            streamingState={streamingState}
            isLoading={isLoading}
            isStreaming={isStreaming}
            streamingContent={streamingContent}
            error={error}
            connectionStatus={connectionStatus}
            showThinking={showThinking}
            activeThinkingMessageId={activeThinkingMessageId}
            setActiveThinkingMessageId={setActiveThinkingMessageId}
            toggleThinkingDisplay={toggleThinkingDisplay}
            setError={setError}
          />
        </div>

        {/* Input - fixed at bottom with flex-shrink-0 */}
        <div className="flex-shrink-0">
          <InputArea
            newMessage={newMessage}
            setNewMessage={setNewMessage}
            handleSendMessage={handleSendMessage}
            isRecording={isRecording}
            toggleRecording={toggleRecording}
            isDisabled={isStreaming}
          />
        </div>
      </div>

      {/* Vertical Resizer (desktop only) */}
      <div
        className="hidden lg:block cursor-col-resize select-none z-30"
        style={{ width: 8, marginLeft: -4, marginRight: -4 }}
        onMouseDown={() => setIsResizing(true)}
        role="separator"
        aria-orientation="vertical"
        tabIndex={-1}
      >
        <div
          className="h-full w-2 mx-auto bg-gray-200 rounded hover:bg-primary-300 transition-colors"
        />
      </div>

      {/* Process Details Panel */}
      <DetailsSidePanel
        isDesktop={isDesktop}
        isDetailsPanelOpen={isDetailsPanelOpen}
        setIsDetailsPanelOpen={setIsDetailsPanelOpen}
        handlePublish={handlePublish}
        conversationId={conversationId ?? undefined}
        sendMessage={sendSpecificMessage}
      />
    </div>
  );
};

/**
 * ChatPanel component serves as the main chat interface
 * It manages the state and logic for the chat functionality
 * Wrapped with WorkflowProvider to provide workflow context
 */
const ChatPanel: React.FC<ChatPanelProps> = (props) => {
  return (
    <WorkflowProvider>
      <InnerChatPanel {...props} />
    </WorkflowProvider>
  );
};

export default ChatPanel;
