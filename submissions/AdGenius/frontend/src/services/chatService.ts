import apiClient from "./api";
import { getToken, setToken } from "../utils/auth";
import { ChatMessage, SSEToolCall, DraftCampaign } from "../types";
import { v4 as uuidv4 } from "uuid";

// Get the base URL for API calls
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Service to handle chat interactions with the backend
 */
export const chatService = {
  /**
   * Generate a unique message ID for idempotent requests
   * @returns A unique message ID
   */
  generateMessageId(): string {
    // Generate a cryptographically secure random UUID
    const uuid = uuidv4();
    return uuid;
  },

  /**
   * Send a message to the chat API
   * @param message User message
   * @param conversationId Optional conversation ID for continuing a conversation
   * @param title Optional title for new conversations
   * @returns The conversation ID for streaming
   */
  async sendMessage(message: string, conversationId?: string, title?: string) {
    try {
      const response = await apiClient.post("/api/v1/chat/message", {
        message,
        conversation_id: conversationId,
        title,
      });

      return response.data;
    } catch (error) {
      console.error("Failed to send message:", error);
      throw error;
    }
  },

  /**
   * Prepare URL for chat stream
   * @param conversationId The conversation ID
   * @param message The user message
   * @param messageId Optional unique message ID for idempotent requests
   * @returns The URL for creating an EventSource connection
   */
  /**
   * Prepare the chat stream URL using user_message_id and optional message_id
   * @param conversationId The conversation ID
   * @param userMessageId The user_message_id returned from the backend after posting the message
   * @param messageId Optional unique message ID for idempotent requests
   * @returns The URL for creating an EventSource connection
   */
  prepareChatStreamUrl(
    conversationId: string,
    userMessageId: string,
    messageId?: string,
  ) {
    const token = getToken();
    if (!token) {
      throw new Error("No authentication token available");
    }

    // Build the URL with the required parameters
    let url = `${API_BASE_URL}/api/v1/chat/stream/${conversationId}?user_message_id=${encodeURIComponent(userMessageId)}&auth_token=${encodeURIComponent(token)}`;

    // Add message_id if provided
    if (messageId) {
      url += `&message_id=${encodeURIComponent(messageId)}`;
    }

    return url;
  },

  /**
   * Get the stream of chat responses
   * @param conversationId The conversation ID
   * @param message The user message
   * @param messageId Optional unique message ID for idempotent requests
   * @returns An EventSource object for the chat stream
   * @deprecated Use prepareChatStreamUrl instead with the useSSEParser.createEventSourceConnection method
   */
  /**
   * Get the stream of chat responses using user_message_id and optional message_id
   * @param conversationId The conversation ID
   * @param userMessageId The user_message_id returned from the backend after posting the message
   * @param messageId Optional unique message ID for idempotent requests
   * @returns An EventSource object for the chat stream
   */
  getChatStream(
    conversationId: string,
    userMessageId: string,
    messageId?: string,
  ) {
    const url = this.prepareChatStreamUrl(
      conversationId,
      userMessageId,
      messageId,
    );

    // Create a new EventSource connection
    return new EventSource(url);
  },

  /**
   * Parse an SSE event data
   * @param eventData The raw event data string
   * @returns Parsed event object
   */
  parseSSEEvent(eventData: string) {
    try {
      return JSON.parse(eventData);
    } catch (error) {
      console.error("Failed to parse SSE event:", error);
      return {
        event_type: "error",
        data: { content: "Error parsing event data", done: false },
      };
    }
  },

  /**
   * Store the authentication token as both cookie and localStorage
   * @param token The JWT token to store
   */
  storeToken(token: string): void {
    // Store in localStorage (already done by auth.ts)
    setToken(token);

    // Also store as cookie for EventSource requests
    document.cookie = `access_token=${token}; path=/; SameSite=Lax`;
  },

  /**
   * Get conversations for the current user with pagination support
   * @param limit Optional maximum number of conversations to return (default: 20)
   * @param offset Optional pagination offset (default: 0)
   * @returns A list of conversation objects
   */
  async getConversations(limit?: number, offset?: number) {
    try {
      // Build query parameters for pagination
      const params = new URLSearchParams();
      if (limit !== undefined) params.append("limit", limit.toString());
      if (offset !== undefined) params.append("offset", offset.toString());

      const queryString = params.toString();
      const url = `/api/v1/chat/conversations${queryString ? `?${queryString}` : ""}`;

      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      console.error("Failed to get conversations:", error);
      throw error;
    }
  },

  /**
   * Get messages for a specific conversation
   * @param conversationId The conversation ID
   * @returns Details of the conversation including messages
   */
  async getConversationDetails(conversationId: string) {
    try {
      const response = await apiClient.get(
        `/api/v1/chat/conversations/${conversationId}`,
      );
      return response.data;
    } catch (error) {
      console.error("Failed to get conversation details:", error);
      throw error;
    }
  },

  /**
   * Delete a conversation
   * @param conversationId The conversation ID to delete
   * @returns Status message
   */
  async deleteConversation(conversationId: string) {
    try {
      const response = await apiClient.delete(
        `/api/v1/chat/conversations/${conversationId}`,
      );
      return response.data;
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      throw error;
    }
  },

  /**
   * Get paginated messages for a specific conversation
   * @param conversationId The conversation ID
   * @param limit Number of messages to fetch per page
   * @param offset Offset for pagination
   * @returns List of messages
   */
  async getConversationMessages(
    conversationId: string,
    limit: number = 20,
    offset: number = 0,
  ) {
    try {
      const params = new URLSearchParams();
      params.append("limit", limit.toString());
      params.append("offset", offset.toString());
      const url = `/api/v1/chat/conversation/${conversationId}/messages?${params.toString()}`;
      console.log("Fetching messages from URL:", API_BASE_URL + url);
      const response = await apiClient.get(url);
      console.log("API Response data:", response.data);

      // Format the response to ensure it's consistent
      // The API might return an array directly or {messages: [...]}
      let formattedResponse;
      if (Array.isArray(response.data)) {
        // API returned messages array directly
        formattedResponse = { messages: response.data };
        console.log("API returned array directly, wrapping in messages object");
      } else if (
        response.data &&
        typeof response.data === "object" &&
        "messages" in response.data
      ) {
        // API returned {messages: [...]}
        formattedResponse = response.data;
        console.log("API returned messages property as expected");
      } else {
        // Unknown format
        console.warn("Unexpected API response format:", response.data);
        formattedResponse = { messages: [] };
      }

      return formattedResponse;
    } catch (error) {
      console.error("Failed to get conversation messages:", error);
      console.error("Error details:", JSON.stringify(error, null, 2));
      throw error;
    }
  },

  /**
   * Map API message format to UI ChatMessage format
   * @param apiMessages Array of messages from the API
   * @returns Array of ChatMessage objects ready for the UI
   */
  mapApiMessagesToUIFormat(
    apiMessages: Array<
      | {
          id: string;
          created_at: string;
          event_data: {
            type?: string;
            event_type?: string;
            content?: string;
            data?: {
              content?: string;
              reasoning_content?: string;
              tools?: unknown[];
            };
            role?: string;
            timestamp?: string;
            done?: boolean;
          };
        }
      | {
          messages: Array<{
            id: string;
            created_at: string;
            event_data: {
              type?: string;
              event_type?: string;
              content?: string;
              data?: {
                content?: string;
                reasoning_content?: string;
                tools?: unknown[];
              };
              role?: string;
              timestamp?: string;
              done?: boolean;
            };
          }>;
        }
    >,
  ): ChatMessage[] {
    if (!apiMessages || !Array.isArray(apiMessages)) {
      console.log("No messages to map or invalid format");
      return [];
    }

    console.log("Mapping API messages to UI format:", apiMessages);

    // Check if we need to unwrap the response
    // Sometimes the API might wrap the messages array in a messages property
    let messagesToMap: Array<{
      id: string;
      created_at: string;
      event_data: {
        type?: string;
        event_type?: string;
        content?: string;
        data?: {
          content?: string;
          reasoning_content?: string;
          tools?: unknown[];
        };
        role?: string;
        timestamp?: string;
        done?: boolean;
      };
    }> = apiMessages as Array<{
      id: string;
      created_at: string;
      event_data: {
        type?: string;
        event_type?: string;
        content?: string;
        data?: {
          content?: string;
          reasoning_content?: string;
          tools?: unknown[];
        };
        role?: string;
        timestamp?: string;
        done?: boolean;
      };
    }>;
    // Try to unwrap if response is {messages: [...]}
    if (
      apiMessages.length === 1 &&
      typeof apiMessages[0] === "object" &&
      apiMessages[0] !== null &&
      "messages" in apiMessages[0] &&
      Array.isArray((apiMessages[0] as { messages?: unknown }).messages)
    ) {
      const firstItem = apiMessages[0] as {
        messages: Array<{
          id: string;
          created_at: string;
          event_data: {
            type?: string;
            event_type?: string;
            content?: string;
            data?: {
              content?: string;
              reasoning_content?: string;
              tools?: unknown[];
            };
            role?: string;
            timestamp?: string;
            done?: boolean;
          };
        }>;
      };
      messagesToMap = firstItem.messages;
      console.log("Unwrapped messages from response");
    }

    // Sort messages by creation time (oldest first)
    const sortedMessages = [...messagesToMap].sort(
      (a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    );

    const mappedMessages: ChatMessage[] = sortedMessages.map((message) => {
      const { id, created_at, event_data } = message;

      // Additional logs for debugging the structure
      console.log(
        "Processing message:",
        id,
        "event_data type:",
        event_data?.type || event_data?.event_type,
      );

      // User message - matches your example format
      if (event_data?.type === "user_message") {
        return {
          id,
          content: event_data.content ?? "",
          sender: "user" as const,
          timestamp: event_data.timestamp || created_at,
        };
      }

      // Bot/Assistant message - matches your example "RunCompleted" format
      if (event_data?.event_type === "RunCompleted") {
        return {
          id,
          content: event_data.data?.content ?? "",
          sender: "bot" as const,
          timestamp: created_at,
          thinkingProcess: {
            eventType: event_data.event_type,
            reasoning: event_data.data?.reasoning_content ?? null,
            tools: (event_data.data?.tools ?? []) as SSEToolCall[],
            isComplete: event_data.done === true,
          },
        };
      }

      // Try to handle other possible formats
      if (
        typeof event_data?.content === "string" ||
        (event_data?.data && typeof event_data.data.content === "string")
      ) {
        return {
          id,
          content:
            typeof event_data.content === "string"
              ? event_data.content
              : event_data.data && typeof event_data.data.content === "string"
                ? event_data.data.content
                : "",
          sender:
            event_data.role === "user" || event_data.type === "user_message"
              ? ("user" as const)
              : ("bot" as const),
          timestamp: created_at,
          thinkingProcess:
            event_data.data &&
            typeof event_data.data.reasoning_content === "string"
              ? {
                  eventType: event_data.event_type || "unknown",
                  reasoning: event_data.data.reasoning_content,
                  tools: (event_data.data.tools ?? []) as SSEToolCall[],
                  isComplete: event_data.done === true,
                }
              : undefined,
        };
      }

      // Default case (fallback) - should not happen with proper data
      console.warn("Unrecognized message format:", message);
      return {
        id,
        content: "Message format not recognized",
        sender: "bot" as const,
        timestamp: created_at,
      };
    });

    console.log("Mapped UI messages:", mappedMessages);
    return mappedMessages;
  },

  /**
   * Get draft campaigns for a conversation
   * @param conversationId The conversation ID
   * @returns Promise with array of draft campaigns
   */
  async getDraftCampaigns(conversationId: string): Promise<DraftCampaign[]> {
    try {
      const response = await apiClient.get(
        `/api/v1/chat/conversation/${conversationId}/draft_campaigns`,
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching draft campaigns:", error);
      return [];
    }
  },
};
