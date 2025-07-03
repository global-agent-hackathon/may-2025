/**
 * navigate.ts
 * 
 * Navigation functionality for DOM operations
 */

import { CONFIG } from '../config';
import { useAppState } from '../../../../state/store';

/**
 * Navigate to a URL
 */
export async function navigate(payload: { url: string }): Promise<void> {
  const tabId = useAppState.getState().currentTask.tabId;
  const targetUrl = payload.url;
  
  let operationContext = {
    tabId,
    targetUrl,
    initialUrl: '',
    navigationStarted: false,
    listenerRegistered: false,
    timeoutReached: false,
    lastError: null as string | null
  };
  
  return new Promise((resolve, reject) => {
    const { TIMEOUT, WAIT_AFTER_COMPLETE } = CONFIG.NAVIGATION;
    
    // Get initial URL for context
    chrome.tabs.get(tabId, (tab) => {
      if (tab?.url) {
        operationContext.initialUrl = tab.url;
      }
    });
    
    // Create listener for navigation completion
    const listener = (updatedTabId: number, changeInfo: chrome.tabs.TabChangeInfo) => {
      // Listen for the tab to finish loading
      if (updatedTabId === tabId && changeInfo.status === 'complete') {
        chrome.tabs.onUpdated.removeListener(listener);
        clearTimeout(timeoutId);
        setTimeout(resolve, WAIT_AFTER_COMPLETE);
      }
    };
    
    // Set a timeout to prevent hanging if navigation fails
    const timeoutId = setTimeout(() => {
      operationContext.timeoutReached = true;
      chrome.tabs.onUpdated.removeListener(listener);
      
      // Try to get current tab state for better error reporting
      chrome.tabs.get(tabId, (tab) => {
        const currentUrl = tab?.url || 'unknown';
        const currentStatus = tab?.status || 'unknown';
        
        operationContext.lastError = `Navigation timeout after ${TIMEOUT / 1000}s. Current URL: ${currentUrl}, Status: ${currentStatus}`;
        reject(new Error(buildNavigateErrorMessage(operationContext)));
      });
    }, TIMEOUT);
    
    // Register listener for tab updates
    operationContext.listenerRegistered = true;
    chrome.tabs.onUpdated.addListener(listener);
    
    // Start the navigation
    operationContext.navigationStarted = true;
    chrome.tabs.update(tabId, { url: targetUrl }, (tab) => {
      if (chrome.runtime.lastError) {
        chrome.tabs.onUpdated.removeListener(listener);
        clearTimeout(timeoutId);
        operationContext.lastError = `Chrome tabs.update failed: ${chrome.runtime.lastError.message}`;
        reject(new Error(buildNavigateErrorMessage(operationContext)));
      }
    });
  });
}

/**
 * Build a detailed error message for navigation failures
 */
function buildNavigateErrorMessage(context: any): string {
  let message = `Navigation operation failed. `;
  
  // Add URL information
  message += `Target URL: ${context.targetUrl}. `;
  if (context.initialUrl) {
    message += `Initial URL: ${context.initialUrl}. `;
  }
  
  // Add tab information
  message += `Tab ID: ${context.tabId}. `;
  
  // Add operation status
  if (context.navigationStarted) {
    message += 'Navigation: ✓ Started. ';
  } else {
    message += 'Navigation: ✗ Never started. ';
  }
  
  if (context.listenerRegistered) {
    message += 'Listener: ✓ Registered. ';
  } else {
    message += 'Listener: ✗ Not registered. ';
  }
  
  if (context.timeoutReached) {
    message += 'Timeout: ✗ Reached. ';
  } else {
    message += 'Timeout: ✓ Within limits. ';
  }
  
  // Add the last error
  if (context.lastError) {
    message += `Error: ${context.lastError}`;
  }
  
  return message;
} 