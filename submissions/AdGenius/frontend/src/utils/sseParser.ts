// Utility for parsing and handling Server-Sent Events (SSE)
import { SSEEvent } from '../types';

/**
 * Parse a raw SSE data string into a structured event object
 */
export function parseSSEEvent(eventData: string): SSEEvent | null {
  try {
    return JSON.parse(eventData);
  } catch (error) {
    console.error('Failed to parse SSE event:', error);
    return null;
  }
}

/**
 * Extract contents from an SSE event 
 */
export function getEventContent(event: SSEEvent): string {
  if (!event || !event.data) return '';
  
  return event.data.content || '';
}

/**
 * Check if an SSE event indicates the stream is complete
 */
export function isStreamComplete(event: SSEEvent): boolean {
  return event?.done === true || event?.event_type === 'RunCompleted';
}

/**
 * Extract reasoning content from an SSE event if available
 */
export function getReasoningContent(event: SSEEvent): string | null {
  if (!event || !event.data) return null;
  
  return event.data.reasoning_content || null;
}

/**
 * Get a human-readable name for an event type
 */
export function getEventTypeName(eventType: string): string {
  switch (eventType) {
    case 'RunStarted':
      return 'Starting';
    case 'ToolCallStarted':
      return 'Tool Call';
    case 'ReasoningStarted':
      return 'Reasoning';
    case 'ReasoningStep':
      return 'Thinking';
    case 'ToolCallCompleted':
      return 'Tool Response';
    case 'RunResponse':
      return 'Response';
    case 'RunCompleted':
      return 'Completed';
    default:
      return eventType || '';
  }
}