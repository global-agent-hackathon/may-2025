export enum WorkflowStatus {
  Pending = "pending",
  InProgress = "in-progress",
  Completed = "completed",
  Failed = "failed",
}

export interface WorkflowStep {
  id: string;
  name: string;
  status: WorkflowStatus;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: string;
  image?: string;
  thinkingProcess?: {
    eventType: string | null;
    reasoning: string | null;
    tools: SSEToolCall[];
    isComplete: boolean;
  };
}

export interface AdRequirement {
  product: string;
  targetAudience: {
    region: string;
    ageRange: string;
    gender: string;
  };
  platform: string;
  budget: number;
  kpi?: string;
}

export interface PublishedCampaignData {
  campaign_id: string;
  campaign_name: string;
  product_name: string;
  ad_id: string;
  ad_title: string;
  ad_status: string;
  ad_url: string;
  status: string;
  publication_date: string;
  publisher_id: string;
  ad_metrics: {
    id: string;
    impressions: number;
    clicks: number;
    conversions: number;
    createdAt: string;
    updatedAt: string;
    advertisementId: string;
  };
}

export interface DraftCampaign {
  id: string;
  conversation_id: string;
  type: "requirements" | "ad_copy" | "ad_image" | "published_campaign";
  data: Record<string, any> | PublishedCampaignData;
  created_at: string;
  updated_at: string;
}

// New types for the AI Chat Assistant
export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
  type: string;
}

export interface ToolResult {
  tool_call_id: string;
  result: unknown;
  type: string;
}

export interface AIMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  tool_calls?: ToolCall[];
  tool_results?: ToolResult[];
}

export interface SSEToolCall {
  content: string;
  tool_call_id: string;
  tool_name: string;
  tool_args: Record<string, unknown>;
  tool_call_error: boolean;
  metrics?: {
    time: number;
    [key: string]: unknown;
  };
  created_at: number;
}

export interface SSEEvent {
  event_type: string;
  data: {
    content: string;
    content_type: string;
    event: string;
    model: string;
    run_id: string;
    agent_id: string;
    session_id: string;
    tools?: SSEToolCall[];
    created_at: number;
    done: boolean;
    reasoning_content?: string;
  };
  done: boolean;
}

export type ConnectionStatus =
  | "disconnected"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "failed";

export interface StreamingState {
  isStreaming: boolean;
  content: string;
  currentEventType: string | null;
  tools: SSEToolCall[];
  reasoning: string | null;
  isDone: boolean;
  messageId: string | null;
}

export interface ConversationDetails {
  conversation: Conversation;
  messages: AIMessage[];
}
