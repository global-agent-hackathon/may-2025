/**
 * ScriptingMode.ts - Compatibility Layer
 * 
 * This file serves as a compatibility layer for the refactored Operation modules.
 * It imports from the new modular structure and re-exports in the expected format
 * to maintain backward compatibility with existing code.
 */

import { useAppState } from '../../state/store';
import { 
  click, 
  setValue, 
  navigate, 
  waiting,
  executeScript,
  type ActionName, 
  type ActionPayload, 
  type ActionResult 
} from './Operation';
import { actionStateManager } from './actionStateManager';

// ==================== Re-export Types ====================

export type { ActionName, ActionPayload, ActionResult };

// ==================== Compatibility Exports ====================

/**
 * DOM action handlers exposed for external use
 * @deprecated - Use individual imports from './Operation' instead
 */
export const domActions = {
  click,
  setValue,
  navigate,
  waiting,
};

/**
 * Primary entry point for calling DOM actions with enhanced logging and error handling
 */
export async function callDOMAction<T extends ActionName>(
  type: T,
  payload: ActionPayload<T>
): Promise<ActionResult> {
  const actionId = `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const startTime = Date.now();
  let actionContext = {
    type,
    payload: JSON.stringify(payload),
    startTime,
    duration: 0,
    tabId: useAppState.getState().currentTask.tabId,
    userAgent: '',
    url: ''
  };

  // Start tracking the action
  actionStateManager.startAction(actionId, type);

  try {
    // Get additional context for error reporting
    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tabs[0]) {
        actionContext.url = tabs[0].url || 'unknown';
      }
      
      // Get user agent for browser context
      try {
        const userAgent = await executeScript(() => navigator.userAgent);
        actionContext.userAgent = String(userAgent || '');
      } catch (e) {
        actionContext.userAgent = '';
      }
    } catch (contextError) {
      // Context gathering failed, but continue with the action
      console.warn('Failed to gather action context:', contextError);
    }

    // Mark action as in progress
    actionStateManager.setActionInProgress(actionId);

    // Type assertion to handle TypeScript's constraints with dynamic method calls
    const action = domActions[type] as (payload: ActionPayload<T>) => Promise<void>;
    
    if (!action) {
      throw new Error(`Unknown action type: ${type}. Available actions: ${Object.keys(domActions).join(', ')}`);
    }
    
    // Execute the action
    await action(payload);
    
    actionContext.duration = Date.now() - startTime;
    console.log(`DOM action ${type} completed successfully in ${actionContext.duration}ms`);
    
    // Mark action as completed
    actionStateManager.completeAction(actionId, {
      type,
      payload,
      context: actionContext
    });

    return {
      success: true,
      actionId,
      duration: actionContext.duration,
      details: {
        type,
        payload,
        context: actionContext
      }
    };
    
  } catch (error: any) {
    actionContext.duration = Date.now() - startTime;
    
    console.error(`Error executing ${type} action:`, error);
    
    // Build a comprehensive error message with context
    let errorMessage = `DOM Action failed: ${type.toUpperCase()} operation unsuccessful. `;
    
    // Add timing information
    errorMessage += `Duration: ${actionContext.duration}ms. `;
    
    // Add tab and browser context
    if (actionContext.tabId) {
      errorMessage += `Tab ID: ${actionContext.tabId}. `;
    }
    
    if (actionContext.url && actionContext.url !== 'unknown') {
      try {
        const urlObj = new URL(actionContext.url);
        errorMessage += `Domain: ${urlObj.hostname}. `;
      } catch (e) {
        errorMessage += `URL: ${actionContext.url}. `;
      }
    }
    
    // Add action-specific context
    if (type === 'click' && typeof payload === 'object' && 'elementId' in payload) {
      errorMessage += `Element ID: ${(payload as any).elementId}. `;
    } else if (type === 'setValue' && typeof payload === 'object' && 'elementId' in payload) {
      const setValuePayload = payload as any;
      errorMessage += `Element ID: ${setValuePayload.elementId}. `;
      if (setValuePayload.value) {
        const valuePreview = setValuePayload.value.length > 50 
          ? setValuePayload.value.substring(0, 50) + '...' 
          : setValuePayload.value;
        errorMessage += `Value length: ${setValuePayload.value.length} chars, Preview: "${valuePreview}". `;
      }
    } else if (type === 'navigate' && typeof payload === 'object' && 'url' in payload) {
      errorMessage += `Target URL: ${(payload as any).url}. `;
    }
    
    // Add browser context if available
    if (actionContext.userAgent) {
      const browserInfo = actionContext.userAgent.includes('Chrome') ? 'Chrome' :
                         actionContext.userAgent.includes('Firefox') ? 'Firefox' :
                         actionContext.userAgent.includes('Safari') ? 'Safari' : 'Unknown';
      errorMessage += `Browser: ${browserInfo}. `;
    }
    
    // Add the underlying error details
    const originalError = error instanceof Error ? error.message : String(error);
    
    // Check if this is already one of our detailed errors
    if (originalError.includes('operation failed for element') || 
        originalError.includes('Navigation operation failed')) {
      // If it's already detailed, just add our context prefix
      errorMessage += `Details: ${originalError}`;
    } else {
      // If it's a generic error, provide more context
      errorMessage += `Underlying error: ${originalError}`;
    }

    // Mark action as failed
    actionStateManager.failAction(actionId, errorMessage);

    return {
      success: false,
      actionId,
      duration: actionContext.duration,
      error: errorMessage,
      details: {
        type,
        payload,
        context: actionContext,
        originalError
      }
    };
  }
}

/**
 * Wait for any currently active action to complete
 */
export async function waitForActionCompletion(): Promise<void> {
  return actionStateManager.waitForAllActions();
}

/**
 * Check if any action is currently in progress
 */
export function hasActiveAction(): boolean {
  return actionStateManager.hasActiveAction();
}

