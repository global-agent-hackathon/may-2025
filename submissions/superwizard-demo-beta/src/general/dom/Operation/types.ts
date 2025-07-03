/**
 * types.ts
 * 
 * TypeScript interfaces and types for DOM operations
 */

export type ActionName = 'click' | 'setValue' | 'navigate' | 'waiting';

export type ActionPayload<T extends ActionName> = T extends 'click' 
  ? { elementId: number }
  : T extends 'setValue'
  ? { elementId: number; value: string }
  : T extends 'navigate'
  ? { url: string }
  : T extends 'waiting'
  ? { seconds: number }
  : never;

// Action completion callback type
export type ActionCompletionCallback = (success: boolean, error?: string) => void;

// Action state tracking
export interface ActionState {
  id: string;
  type: ActionName;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  startTime: number;
  endTime?: number;
  error?: string;
}

// Enhanced action result
export interface ActionResult {
  success: boolean;
  actionId: string;
  duration: number;
  error?: string;
  details?: any;
}

export interface ElementCoordinates {
  x: number;
  y: number;
}

export interface ElementVisibilityResult {
  success: boolean;
  fullyVisible?: boolean;
  reason?: string;
  rect?: DOMRect;
}

export interface SetValueResult {
  success: boolean;
  type?: string;
  reason?: string;
}

export interface PageStabilityData {
  elementCount: number;
  loadingElements: number;
  pendingXHR: number;
  pendingFetch: number;
  readyState: string;
  bodyHeight: number;
  runningAnimations: number;
  mutationCount: number;
  url: string;
}

export interface ClickResult {
  success: boolean;
  reason?: string;
  method?: string;
}

export interface ScrollResult {
  success: boolean;
  reason?: string;
  position?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  isFullyVisible?: boolean;
  isPartiallyVisible?: boolean;
  madeProgress?: boolean;
}

export interface WaitingResult {
  success: boolean;
  waitedSeconds: number;
  reason?: string;
} 