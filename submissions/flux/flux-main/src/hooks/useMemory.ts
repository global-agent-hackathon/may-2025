import { useState, useCallback } from "react";
import { useUser } from "@clerk/clerk-react";
import {
  memoryService,
  MemorySearchRequest,
  MemorySearchResponse,
  AddConversationMemoryRequest,
  AddFormInteractionMemoryRequest,
  AddUserPreferenceMemoryRequest,
  MemoryOperationResponse,
  UserContextResponse,
  FormHistoryResponse,
  UserPreferencesResponse,
  trackFormInteraction,
  trackUserPreference,
  getRelevantContext,
} from "@/lib/memory";

export function useMemory() {
  const { user } = useUser();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const userId = user?.id;

  const searchMemories = useCallback(
    async (query: string, limit?: number, memoryType?: string): Promise<MemorySearchResponse | null> => {
      if (!userId) return null;

      setLoading(true);
      setError(null);

      try {
        // Validate query is not empty
        const cleanQuery = (query || "").trim();
        if (!cleanQuery) {
          console.warn("Empty query provided to searchMemories");
          setError("Search query cannot be empty");
          return {
            memories: [],
            total_count: 0
          };
        }

        const request: MemorySearchRequest = {
          user_id: userId,
          query: cleanQuery,
          limit,
          memory_type: memoryType,
        };

        console.log(`Making memory search request:`, request);
        const response = await memoryService.searchMemories(request);
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to search memories";
        console.error("Memory search error:", errorMessage);
        setError(errorMessage);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  const addConversationMemory = useCallback(
    async (
      userMessage: string,
      assistantResponse: string,
      context?: Record<string, any>
    ): Promise<boolean> => {
      if (!userId) return false;

      try {
        const request: AddConversationMemoryRequest = {
          user_id: userId,
          user_message: userMessage,
          assistant_response: assistantResponse,
          context,
        };

        const response = await memoryService.addConversationMemory(request);
        return response.success;
      } catch (err) {
        console.warn("Failed to add conversation memory:", err);
        return false;
      }
    },
    [userId]
  );

  const addFormInteractionMemory = useCallback(
    async (
      formId: string,
      formTitle: string,
      interactionType: string,
      details: Record<string, any>
    ): Promise<boolean> => {
      if (!userId) return false;

      try {
        const request: AddFormInteractionMemoryRequest = {
          user_id: userId,
          form_id: formId,
          form_title: formTitle,
          interaction_type: interactionType,
          details,
        };

        const response = await memoryService.addFormInteractionMemory(request);
        return response.success;
      } catch (err) {
        console.warn("Failed to add form interaction memory:", err);
        return false;
      }
    },
    [userId]
  );

  const addUserPreferenceMemory = useCallback(
    async (
      preferenceType: string,
      preferenceValue: any,
      context?: string
    ): Promise<boolean> => {
      if (!userId) return false;

      try {
        const request: AddUserPreferenceMemoryRequest = {
          user_id: userId,
          preference_type: preferenceType,
          preference_value: preferenceValue,
          context,
        };

        const response = await memoryService.addUserPreferenceMemory(request);
        return response.success;
      } catch (err) {
        console.warn("Failed to add user preference memory:", err);
        return false;
      }
    },
    [userId]
  );

  const getUserContext = useCallback(
    async (query: string): Promise<UserContextResponse | null> => {
      if (!userId) return null;

      setLoading(true);
      setError(null);

      try {
        const response = await memoryService.getUserContext({
          user_id: userId,
          query,
        });
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to get user context";
        setError(errorMessage);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  const getFormHistory = useCallback(
    async (formId?: string): Promise<FormHistoryResponse | null> => {
      if (!userId) return null;

      setLoading(true);
      setError(null);

      try {
        const response = await memoryService.getFormHistory({
          user_id: userId,
          form_id: formId,
        });
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to get form history";
        setError(errorMessage);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  const getUserPreferences = useCallback(async (): Promise<UserPreferencesResponse | null> => {
    if (!userId) return null;

    setLoading(true);
    setError(null);

    try {
      const response = await memoryService.getUserPreferences(userId);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to get user preferences";
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Helper functions
  const trackFormInteractionHelper = useCallback(
    async (
      formId: string,
      formTitle: string,
      interactionType: "created" | "filled" | "analyzed" | "viewed" | "edited",
      details: Record<string, any> = {}
    ) => {
      if (!userId) return;
      await trackFormInteraction(userId, formId, formTitle, interactionType, details);
    },
    [userId]
  );

  const trackUserPreferenceHelper = useCallback(
    async (preferenceType: string, preferenceValue: any, context?: string) => {
      if (!userId) return;
      await trackUserPreference(userId, preferenceType, preferenceValue, context);
    },
    [userId]
  );

  const getRelevantContextHelper = useCallback(
    async (query: string): Promise<string> => {
      if (!userId) return "";
      return await getRelevantContext(userId, query);
    },
    [userId]
  );

  return {
    // State
    loading,
    error,
    userId,

    // Core memory functions
    searchMemories,
    addConversationMemory,
    addFormInteractionMemory,
    addUserPreferenceMemory,
    getUserContext,
    getFormHistory,
    getUserPreferences,

    // Helper functions
    trackFormInteraction: trackFormInteractionHelper,
    trackUserPreference: trackUserPreferenceHelper,
    getRelevantContext: getRelevantContextHelper,
  };
} 