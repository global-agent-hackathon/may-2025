// Chat API Types

export interface ChatThreadWithMessages {
  id: string;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  messages: MessageResponse[];
  message_count?: number;
  last_message?: {
    content: string;
    sender: "user" | "assistant";
    timestamp: string;
  };
}

export interface MessageResponse {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: string;
  iframe_url?: string[];
  metadata?: {
    tools: any[];
    formatted_tool_calls: any[];
    citations: any[];
    messages: {
      role: string;
      content: string;
    }[];
    model: string;
  };
  user_id?: string;
  user_name?: string;
}

export interface SendMessageRequest {
  content: string;
  attachments?: Array<{ id: string }>;
  user_id?: string;
  user_name?: string;
}

export interface CreateThreadResponse {
  thread_id: string;
}

export interface DeleteThreadResponse {
  success: boolean;
}

// Company API Types
export interface Company {
  id: string | number;
  name: string;
  description?: string;
  logo?: string;
  logoUrl?: string;
  logoText?: string;
  logoSubText?: string;
  logoIconClass?: string;
  fundingStage: string;
  tags?: string[];
  fundingAsk?: string | number;
  industry?: string;
  valuation?: string | number;
  location?: string;
  gradientColors?: { from: string; to: string };
}

export interface CompanySearchResult {
  name: string;
  logoUrl: string;
}

// News API Types
export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  source: string[];
  published_at: string;
  category: string;
  image_url: string;
  citations: {
    url: string | null;
    title: string;
  }[];
}

// API Response Types
export interface ApiError {
  error: string;
  message: string;
  status: number;
}

// URL Configuration
export const API_ENDPOINTS = {
  THREADS: '/chat/threads',
  THREAD: (threadId: string) => `/chat/threads/${threadId}`,
  MESSAGES: (threadId: string) => `/chat/threads/${threadId}/messages`,
  FILES_UPLOAD: '/files/upload',
  COMPANIES_SEARCH: '/companies/search',
  COMPANIES_FEATURED: '/companies/featured',
  NEWS_TRENDING: '/news/trending'
}; 