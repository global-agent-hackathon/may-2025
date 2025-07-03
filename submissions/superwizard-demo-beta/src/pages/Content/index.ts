// console.log('Content script loaded..');

import { watchForRPCRequests } from '../../general/browser/pageRPC';
import { CursorSimulator } from './cursor';
import './content.styles.css';

// Initialize based on stored state
console.log('Content script loaded');

// Function to get cursor enabled setting from storage
async function getCursorEnabledSetting(): Promise<boolean> {
  return new Promise((resolve) => {
    chrome.storage.sync.get(['cursorEnabled'], (result) => {
      // Default to true if setting doesn't exist
      resolve(result.cursorEnabled !== false);
    });
  });
}

// Initialize cursor
(async () => {
  try {
    // Wait for DOM to be fully loaded
    if (document.readyState !== 'complete') {
      await new Promise<void>((resolve) => {
        window.addEventListener('load', () => resolve(), { once: true });
      });
    }

    // Check if cursor is enabled in settings
    const cursorEnabled = await getCursorEnabledSetting();
    
    if (!cursorEnabled) {
      console.log('Cursor is disabled in settings, skipping initialization');
      // Ensure no cursor exists
      const existingCursor = (window as any).__superwizardCursor;
      if (existingCursor) {
        existingCursor.destroy();
        (window as any).__superwizardCursor = null;
      }
      return;
    }

    // Remove any existing cursor before creating a new one
    const existingCursor = (window as any).__superwizardCursor;
    if (existingCursor) {
      existingCursor.destroy();
    }

    // Create and initialize cursor
    const cursor = new CursorSimulator({
      size: 16,
      color: '#5C7CFA',
      zIndex: 2147483647
    });
    cursor.initialize();
    
    // Make cursor available globally
    (window as any).__superwizardCursor = cursor;
    console.log('Cursor initialized successfully');
    
    // Add visibility change event listener
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        // Only reinitialize if cursor is still enabled
        getCursorEnabledSetting().then(enabled => {
          if (enabled) {
            const cursorInstance = (window as any).__superwizardCursor;
            if (cursorInstance) {
              cursorInstance.initialize();
            }
          }
        });
      }
    });
    
    // Add window focus event listener 
    window.addEventListener('focus', () => {
      // Only reinitialize if cursor is still enabled
      getCursorEnabledSetting().then(enabled => {
        if (enabled) {
          const cursorInstance = (window as any).__superwizardCursor;
          if (cursorInstance) {
            cursorInstance.initialize();
          }
        }
      });
    });
  } catch (error) {
    console.error('Failed to initialize cursor:', error);
  }
})();

// Watch for RPC requests
watchForRPCRequests();

// Listen for messages from the extension
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Received message:', message.type);
  
  if (message.type === 'PING') {
    console.log('Received PING, responding with PONG');
    sendResponse({ status: 'PONG' });
    return true;
  } else if (message.type === 'SIDEBAR_ACTIVATED') {
    console.log('Sidebar activated');
    sendResponse({ success: true });
    return true; // Required for async response
  } else if (message.type === 'SIDEBAR_DEACTIVATED') {
    console.log('Sidebar deactivated');
    sendResponse({ success: true });
  } else if (message.type === 'UPDATE_CURSOR_STATE') {
    const cursorEnabled = message.enabled;
    console.log('Updating cursor state:', cursorEnabled);
    
    try {
      // Always destroy existing cursor first
      const existingCursor = (window as any).__superwizardCursor;
      if (existingCursor) {
        console.log('Destroying existing cursor instance');
        existingCursor.destroy();
        (window as any).__superwizardCursor = null;
      }
      
      if (cursorEnabled) {
        // Create new cursor instance only if enabled
        console.log('Creating new cursor instance');
        const cursor = new CursorSimulator({
          size: 16,
          color: '#5C7CFA',
          zIndex: 2147483647
        });
        cursor.initialize();
        (window as any).__superwizardCursor = cursor;
        console.log('New cursor initialized successfully');
      }
      
      // Send success response
      sendResponse({ success: true });
    } catch (error: any) {
      console.error('Error updating cursor state:', error);
      sendResponse({ success: false, error: error.message });
    }
  }
  return true; // Required for async response
});
