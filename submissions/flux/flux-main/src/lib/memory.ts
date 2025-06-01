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
    created_at?: string;
    relevanceScore?: number;
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

export class MemoryService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:3000/api";
  }

  private async makeRequest<T>(endpoint: string, method: string = "GET", data?: any): Promise<T> {
    const config: RequestInit = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    // Add authentication headers if available (client-side)
    if (typeof window !== 'undefined') {
      try {
        // Try to get auth token from Clerk's window object
        const clerk = (window as any).Clerk;
        if (clerk && clerk.session) {
          const token = await clerk.session.getToken();
          if (token) {
            config.headers = {
              ...config.headers,
              Authorization: `Bearer ${token}`,
            };
          }
        }
      } catch (error) {
        // Ignore auth errors and proceed without token
        console.warn("Failed to get auth token:", error);
      }
    }

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
export const memoryService = new MemoryService();

// Helper functions for common operations
export async function trackFormInteraction(
  userId: string,
  formId: string,
  formTitle: string,
  interactionType: "created" | "filled" | "analyzed" | "viewed" | "edited",
  details: Record<string, any> = {}
) {
  try {
    await memoryService.addFormInteractionMemory({
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

export async function trackUserPreference(
  userId: string,
  preferenceType: string,
  preferenceValue: any,
  context?: string
) {
  try {
    await memoryService.addUserPreferenceMemory({
      user_id: userId,
      preference_type: preferenceType,
      preference_value: preferenceValue,
      context,
    });
  } catch (error) {
    console.warn("Failed to track user preference:", error);
  }
}

export async function getRelevantContext(userId: string, query: string): Promise<string> {
  try {
    const response = await memoryService.getUserContext({
      user_id: userId,
      query,
    });
    return response.context;
  } catch (error) {
    console.warn("Failed to get user context:", error);
    return "";
  }
}

// Smart keyword extraction for better memory search
export function extractContextualKeywords(prompt: string): string[] {
  // Remove common stop words and extract meaningful terms
  const stopWords = new Set([
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it',
    'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with', 'i', 'want', 'need', 'create',
    'make', 'build', 'design', 'form', 'field', 'add', 'new', 'please', 'can', 'you', 'help', 'me'
  ]);

  // Extract words and filter
  const words = prompt
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ') // Remove punctuation
    .split(/\s+/)
    .filter(word => word.length > 2 && !stopWords.has(word));

  // Identify domain-specific keywords that are more valuable
  const domainKeywords = words.filter(word => {
    return (
      // Business/industry terms
      /^(customer|client|user|employee|staff|team|company|business|organization|department)/.test(word) ||
      // Form types
      /^(feedback|survey|application|registration|contact|order|booking|appointment|evaluation|assessment)/.test(word) ||
      // Field types and concepts
      /^(email|phone|address|name|title|description|rating|score|date|time|number|text|dropdown|checkbox|radio)/.test(word) ||
      // Industries
      /^(healthcare|education|finance|retail|technology|marketing|sales|hr|legal|real|estate)/.test(word) ||
      // Actions and purposes
      /^(collect|gather|track|analyze|measure|evaluate|assess|review|submit|process)/.test(word)
    );
  });

  // Combine domain keywords with other meaningful words, prioritizing domain terms
  const allKeywords = [...new Set([...domainKeywords, ...words])];
  
  // Return top 5-8 most relevant keywords
  return allKeywords.slice(0, 8);
}

// Enhanced memory search with contextual understanding
export async function searchMemoriesWithContext(
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
      console.warn("Empty prompt provided to searchMemoriesWithContext, using fallback");
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

    console.log(`Making memory search request with query: "${searchQuery}"`);

    // Make only ONE API call instead of multiple
    const response = await memoryService.searchMemories({
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
      
      // Boost score for recent memories
      if (memory.created_at) {
        const daysSinceCreated = (Date.now() - new Date(memory.created_at).getTime()) / (1000 * 60 * 60 * 24);
        if (daysSinceCreated < 30) score += 1;
      }
      
      // Boost score for successful forms
      if (memory.metadata?.ai_form_analytics?.success_score >= 7) {
        score += 3;
      }
      
      return { ...memory, relevanceScore: score };
    });

    // Sort by relevance and return results
    const topResults = scoredResults
      .sort((a, b) => b.relevanceScore - a.relevanceScore)
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

// Enhanced context retrieval for AI form generation
export async function getEnhancedFormContext(
  userId: string,
  prompt: string
): Promise<string> {
  try {
    const keywords = extractContextualKeywords(prompt);
    
    // Search for relevant form creation patterns
    const memories = await searchMemoriesWithContext(userId, prompt, 5, "form_interaction");
    
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

    // Add specific recommendations based on keywords
    if (keywords.includes('feedback') || keywords.includes('survey')) {
      insights.push("Consider including rating scales and open-ended comment fields");
    }
    
    if (keywords.includes('application') || keywords.includes('job')) {
      insights.push("Include file upload for resume/documents and structured experience fields");
    }
    
    if (keywords.includes('registration') || keywords.includes('event')) {
      insights.push("Add date/time fields and contact information collection");
    }

    return insights.length > 0 
      ? `Memory insights: ${insights.join('. ')}.`
      : "";

  } catch (error) {
    console.warn("Failed to get enhanced form context:", error);
    return "";
  }
} 