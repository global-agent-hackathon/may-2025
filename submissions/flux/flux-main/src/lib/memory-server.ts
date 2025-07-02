import { auth } from "@clerk/nextjs/server";
import { extractContextualKeywords } from "./memory";

const AGENT_API_URL = process.env.AGENT_API_URL || "http://localhost:8000";

export interface MemorySearchRequest {
  user_id: string;
  query: string;
  limit?: number;
  memory_type?: string;
}

export interface MemorySearchResponse {
  memories: Array<{
    memory: string;
    metadata?: Record<string, any>;
  }>;
  total_count: number;
}

export interface AddConversationMemoryRequest {
  user_id: string;
  user_message: string;
  assistant_response: string;
  context?: Record<string, any>;
}

export interface AddFormInteractionMemoryRequest {
  user_id: string;
  form_id: string;
  form_title: string;
  interaction_type: string;
  details: Record<string, any>;
}

export interface AddUserPreferenceMemoryRequest {
  user_id: string;
  preference_type: string;
  preference_value: any;
  context?: string;
}

export interface MemoryOperationResponse {
  success: boolean;
  message: string;
}

export interface UserContextRequest {
  user_id: string;
  query: string;
}

export interface UserContextResponse {
  context: string;
  memories_count: number;
}

export interface FormHistoryRequest {
  user_id: string;
  form_id?: string;
}

export interface FormHistoryResponse {
  interactions: Array<Record<string, any>>;
  total_count: number;
}

export interface UserPreferencesResponse {
  preferences: Record<string, any>;
  total_count: number;
}

export class MemoryServerService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.AGENT_API_URL || "http://localhost:8000";
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    try {
      // Get the auth token from Clerk
      const { getToken } = await auth();
      const token = await getToken();
      
      return {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      };
    } catch (error) {
      console.warn("Failed to get auth token:", error);
      return {
        "Content-Type": "application/json",
      };
    }
  }

  private async makeRequest<T>(endpoint: string, method: string = "GET", data?: any): Promise<T> {
    const headers = await this.getAuthHeaders();
    
    const config: RequestInit = {
      method,
      headers,
    };

    if (data && method !== "GET") {
      config.body = JSON.stringify(data);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, config);

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication required");
      }
      if (response.status === 403) {
        throw new Error("Access denied");
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async searchMemories(request: MemorySearchRequest): Promise<MemorySearchResponse> {
    return this.makeRequest<MemorySearchResponse>("/memory/search", "POST", request);
  }

  async addConversationMemory(request: AddConversationMemoryRequest): Promise<MemoryOperationResponse> {
    return this.makeRequest<MemoryOperationResponse>("/memory/conversation", "POST", request);
  }

  async addFormInteractionMemory(request: AddFormInteractionMemoryRequest): Promise<MemoryOperationResponse> {
    return this.makeRequest<MemoryOperationResponse>("/memory/form-interaction", "POST", request);
  }

  async addUserPreferenceMemory(request: AddUserPreferenceMemoryRequest): Promise<MemoryOperationResponse> {
    return this.makeRequest<MemoryOperationResponse>("/memory/user-preference", "POST", request);
  }

  async getUserContext(request: UserContextRequest): Promise<UserContextResponse> {
    return this.makeRequest<UserContextResponse>("/memory/user-context", "POST", request);
  }

  async getFormHistory(request: FormHistoryRequest): Promise<FormHistoryResponse> {
    return this.makeRequest<FormHistoryResponse>("/memory/form-history", "POST", request);
  }

  async getUserPreferences(userId: string): Promise<UserPreferencesResponse> {
    return this.makeRequest<UserPreferencesResponse>(`/memory/user-preferences/${userId}`);
  }
}

// Singleton instance
export const memoryServerService = new MemoryServerService();

// Helper functions for common operations (server-side)
export async function trackFormInteractionServer(
  userId: string,
  formId: string,
  formTitle: string,
  interactionType: "created" | "filled" | "analyzed" | "viewed" | "edited",
  details: Record<string, any> = {}
) {
  try {
    await memoryServerService.addFormInteractionMemory({
      user_id: userId,
      form_id: formId,
      form_title: formTitle,
      interaction_type: interactionType,
      details,
    });
  } catch (error) {
    console.warn("Failed to track form interaction:", error);
  }
}

export async function trackUserPreferenceServer(
  userId: string,
  preferenceType: string,
  preferenceValue: any,
  context?: string
) {
  try {
    await memoryServerService.addUserPreferenceMemory({
      user_id: userId,
      preference_type: preferenceType,
      preference_value: preferenceValue,
      context,
    });
  } catch (error) {
    console.warn("Failed to track user preference:", error);
  }
}

export async function getRelevantContextServer(userId: string, query: string): Promise<string> {
  try {
    const response = await memoryServerService.getUserContext({
      user_id: userId,
      query,
    });
    return response.context;
  } catch (error) {
    console.warn("Failed to get user context:", error);
    return "";
  }
}

// Enhanced context retrieval for AI form generation (server-side)
export async function getEnhancedFormContextServer(
  userId: string,
  prompt: string
): Promise<string> {
  try {
    // Search for relevant form creation patterns
    const memories = await memoryServerService.searchMemories({
      user_id: userId,
      query: prompt,
      limit: 5,
      memory_type: "form_interaction"
    });
    
    if (!memories?.memories?.length) return "";

    // Build contextual insights
    const insights: string[] = [];
    
    // Analyze successful patterns
    const successfulForms = memories.memories.filter(m => 
      m.metadata?.ai_form_analytics?.success_score >= 7
    );
    
    if (successfulForms.length > 0) {
      const avgFields = successfulForms.reduce((acc, m) => 
        acc + (m.metadata?.ai_form_analytics?.generated_field_count || 0), 0
      ) / successfulForms.length;
      
      insights.push(`Similar successful forms averaged ${Math.round(avgFields)} fields`);
      
      // Extract common field types
      const fieldTypes = successfulForms.flatMap(m => 
        m.metadata?.ai_form_analytics?.generated_field_types || []
      );
      const popularTypes = [...new Set(fieldTypes)].slice(0, 3);
      
      if (popularTypes.length > 0) {
        insights.push(`Popular field types for similar forms: ${popularTypes.join(', ')}`);
      }
    }

    return insights.length > 0 
      ? `Memory insights: ${insights.join('. ')}.`
      : "";

  } catch (error) {
    console.warn("Failed to get enhanced form context:", error);
    return "";
  }
}

// Enhanced memory search with contextual understanding (server-side)
export async function searchMemoriesWithContextServer(
  userId: string,
  prompt: string,
  limit: number = 10,
  memoryType?: string
): Promise<MemorySearchResponse | null> {
  try {
    // Ensure prompt is not empty or undefined
    const cleanPrompt = (prompt || "").trim();
    
    // If prompt is empty, use a default safe query
    if (!cleanPrompt) {
      console.warn("Empty prompt provided to searchMemoriesWithContextServer, using fallback");
      return {
        memories: [],
        total_count: 0
      };
    }
    
    const keywords = extractContextualKeywords(cleanPrompt);
    
    // Create a single optimized search query instead of multiple calls
    let searchQuery = `${cleanPrompt} ${keywords.slice(0, 3).join(' ')}`.trim();
    
    // Ensure query is not empty or just whitespace
    if (!searchQuery || searchQuery.trim().length < 3) {
      console.log("Query too short, using fallback query");
      searchQuery = "recent form interactions";
    }

    console.log(`Making server memory search request with query: "${searchQuery}"`);

    // Make only ONE API call instead of multiple
    const response = await memoryServerService.searchMemories({
      user_id: userId,
      query: searchQuery,
      limit: limit,
      memory_type: memoryType
    });

    if (!response.memories?.length) {
      return {
        memories: [],
        total_count: 0
      };
    }

    // Score results based on keyword matches and recency
    const scoredResults = response.memories.map(memory => {
      let score = 0;
      const memoryText = memory.memory.toLowerCase();
      
      // Score based on keyword matches
      keywords.forEach(keyword => {
        if (memoryText.includes(keyword.toLowerCase())) {
          score += 2;
        }
      });
      
      // Boost score for successful forms
      if (memory.metadata?.ai_form_analytics?.success_score >= 7) {
        score += 3;
      }
      
      return { ...memory, relevanceScore: score };
    });

    // Sort by relevance and return results
    const topResults = scoredResults
      .sort((a, b) => (b.relevanceScore || 0) - (a.relevanceScore || 0))
      .slice(0, limit);

    return {
      memories: topResults,
      total_count: topResults.length
    };
  } catch (error) {
    console.warn("Enhanced memory search failed:", error);
    return null;
  }
} 