import { useState, useCallback, useRef, useEffect } from "react";
import { StreamingState, ConnectionStatus } from "../types";
import {
  parseSSEEvent,
  getEventContent,
  isStreamComplete,
  getReasoningContent,
  getEventTypeName,
} from "../utils/sseParser";

/**
 * Hook for parsing Server-Sent Events (SSE) from the backend
 */
export default function useSSEParser() {
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    content: "",
    currentEventType: null,
    tools: [],
    reasoning: null,
    isDone: false,
    messageId: null,
  });

  // Keep track of connection state and retries
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatus>("disconnected");
  const eventSourceRef = useRef<EventSource | null>(null);
  const retriesRef = useRef<number>(0);
  const maxRetries = 3;
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );

  // Close the EventSource connection safely
  const closeConnection = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      closeConnection();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [
    closeConnection,
    setConnectionStatus,
    setConnectionError,
    setStreamingState,
  ]);

  const resetStreamingState = useCallback(() => {
    setStreamingState({
      isStreaming: false,
      content: "",
      currentEventType: null,
      tools: [],
      reasoning: null,
      isDone: false,
      messageId: null,
    });
    setConnectionError(null);
    setConnectionStatus("disconnected");
    retriesRef.current = 0;
  }, [setStreamingState, setConnectionError, setConnectionStatus]);

  // Special function to maintain state but mark as complete
  const markStreamingComplete = useCallback(() => {
    setStreamingState((prev) => ({
      ...prev,
      isStreaming: false,
      isDone: true,
    }));
    closeConnection();
  }, [setStreamingState, closeConnection]);

  const startStreaming = useCallback(
    (messageId: string | null = null) => {
      setStreamingState((prev) => ({
        ...prev,
        isStreaming: true,
        content: "",
        currentEventType: null,
        tools: [],
        reasoning: null,
        isDone: false,
        messageId,
      }));
      setConnectionError(null);
      setConnectionStatus("disconnected");
      retriesRef.current = 0;
    },
    [setStreamingState, setConnectionError, setConnectionStatus],
  );

  const handleSSEEvent = useCallback(
    (eventData: string) => {
      try {
        const sseEvent = parseSSEEvent(eventData);
        if (!sseEvent) return null;

        // Reset error state and update connection status on successful event
        // This ensures we clear any connection error messages when we receive data
        if (connectionError || connectionStatus !== "connected") {
          console.log("Connection restored - message received");
          setConnectionError(null);
          setConnectionStatus("connected");
          retriesRef.current = 0;
        }

        // Handle different event types
        switch (sseEvent.event_type) {
          case "RunResponse": {
            // Process actual response content
            const content = getEventContent(sseEvent);
            if (content) {
              setStreamingState((prev) => ({
                ...prev,
                content: prev.content + content,
                isDone: isStreamComplete(sseEvent),
              }));
            }
            break;
          }

          case "RunStarted":
          case "ToolCallStarted":
          case "ReasoningStarted": {
            setStreamingState((prev) => ({
              ...prev,
              currentEventType: getEventTypeName(sseEvent.event_type),
            }));
            break;
          }

          case "ReasoningStep": {
            const reasoning = getReasoningContent(sseEvent);
            if (reasoning) {
              setStreamingState((prev) => ({
                ...prev,
                reasoning: reasoning,
                currentEventType: getEventTypeName(sseEvent.event_type),
              }));
            }
            break;
          }

          case "ToolCallCompleted": {
            if (sseEvent.data && sseEvent.data.tools) {
              setStreamingState((prev) => ({
                ...prev,
                tools: Array.isArray(sseEvent.data.tools)
                  ? [...sseEvent.data.tools]
                  : [],
                currentEventType: getEventTypeName(sseEvent.event_type),
              }));
            }
            break;
          }

          case "RunCompleted": {
            if (sseEvent.done) {
              const finalContent = sseEvent.data?.content || "";
              setStreamingState((prev) => ({
                ...prev,
                isDone: true,
                content: prev.content + finalContent,
              }));
              closeConnection();
            }
            break;
          }
        }

        return sseEvent;
      } catch (error) {
        console.error("Error processing SSE event:", error);
        setConnectionError(
          `Error processing event: ${error instanceof Error ? error.message : "Unknown error"}`,
        );
        return null;
      }
    },
    [
      connectionError,
      connectionStatus,
      closeConnection,
      setConnectionError,
      setConnectionStatus,
      setStreamingState,
    ],
  );

  const completeStreaming = useCallback(() => {
    setStreamingState((prev) => ({
      ...prev,
      isStreaming: false,
      isDone: true,
      // Note: We preserve reasoning, tools, and other data for displaying later
    }));
    closeConnection();
  }, [setStreamingState, closeConnection]);

  // Helper function to safely get content from the streaming state
  const getStreamingContent = useCallback(() => {
    return streamingState.content || "";
  }, [streamingState.content]);

  // Create and configure an EventSource connection with retry logic
  const createEventSourceConnection = useCallback(
    (
      url: string,
      onMessage: (event: MessageEvent) => void,
      onStreamComplete?: () => void,
    ) => {
      // Close any existing connection first
      closeConnection();

      // Update connection status to connecting
      setConnectionStatus("connecting");

      try {
        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
          try {
            // Process the event
            onMessage(event);

            // Check if this is a completion event
            const data = JSON.parse(event.data);
            if (data.event_type === "RunCompleted" && data.done) {
              // Call the onStreamComplete callback if provided
              if (onStreamComplete) {
                onStreamComplete();
              }
            }
          } catch (error) {
            console.error("Error processing message:", error);
          }
        };

        // Check for X-Message-ID header when connecting
        eventSource.onopen = () => {
          try {
            // Update messageId if available in the response headers
            if (eventSource.url) {
              const messageIdParam = new URL(eventSource.url).searchParams.get(
                "message_id",
              );
              if (messageIdParam) {
                setStreamingState((prev) => ({
                  ...prev,
                  messageId: messageIdParam,
                }));
                console.log("Connected with message ID:", messageIdParam);
              }
            }
          } catch (error) {
            console.error("Error processing message ID:", error);
          }
          console.log("Connection established/reestablished successfully");
          setConnectionStatus("connected");
          setConnectionError(null);
          retriesRef.current = 0;
        };

        eventSource.onerror = (error) => {
          console.error("EventSource connection error:", error);

          // Prevent retry if stream ended normally (done: true)
          // If the streamingState is marked as done, do not retry
          if (streamingState.isDone) {
            console.log("Stream ended normally (done: true), not retrying.");
            closeConnection();
            return;
          }

          // Only attempt reconnection if we haven't exceeded max retries
          if (retriesRef.current < maxRetries) {
            retriesRef.current++;
            const retryMessage = `Connection lost. Retry attempt ${retriesRef.current}/${maxRetries}...`;
            console.log(retryMessage);
            setConnectionError(retryMessage);
            setConnectionStatus("reconnecting");

            // Close the current connection
            closeConnection();

            // Exponential backoff for retries: 1s, 2s, 4s
            const retryDelay = Math.pow(2, retriesRef.current - 1) * 1000;

            reconnectTimeoutRef.current = setTimeout(() => {
              console.log(
                `Retrying connection (${retriesRef.current}/${maxRetries})...`,
              );
              const newEventSource = createEventSourceConnection(
                url,
                onMessage,
              );

              // If we successfully created a new connection, return it
              if (newEventSource) {
                return;
              }
            }, retryDelay);
          } else {
            const finalErrorMsg =
              "Connection lost. Maximum retry attempts reached.";
            console.log(finalErrorMsg);
            setConnectionError(finalErrorMsg);
            setConnectionStatus("failed");
            setStreamingState((prev) => ({
              ...prev,
              isStreaming: false,
              isDone: false,
            }));
            closeConnection();
          }
        };

        return eventSource;
      } catch (error) {
        console.error("Failed to create EventSource:", error);
        setConnectionError(
          `Failed to establish connection: ${error instanceof Error ? error.message : "Unknown error"}`,
        );
        setConnectionStatus("failed");
        return null;
      }
    },
    [closeConnection, streamingState.isDone],
  );

  return {
    streamingState,
    connectionError,
    connectionStatus,
    setStreamingState,
    resetStreamingState,
    startStreaming,
    handleSSEEvent,
    completeStreaming,
    markStreamingComplete,
    getStreamingContent,
    createEventSourceConnection,
    closeConnection,
  };
}
