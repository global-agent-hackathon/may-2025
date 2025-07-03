/**
 * cursor.ts
 * 
 * Cursor management and simulation for DOM operations
 */

import { useAppState } from '../../../../state/store';
import { CONFIG } from '../config';

/**
 * Module scope variable to track cursor state
 */
let cursorEnabled: boolean | null = null;

/**
 * Execute a function in the context of the active tab
 */
async function executeScript<T>(func: (...args: any[]) => T, ...args: any[]): Promise<T> {
  const tabId = useAppState.getState().currentTask.tabId;
  
  try {
    const result = await chrome.scripting.executeScript({
      target: { tabId },
      func,
      args
    });
    
    return result[0]?.result as T;
  } catch (error) {
    console.error("Error executing script:", error);
    throw new Error(`Script execution failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Initialize cursor if not already initialized
 */
export async function initializeCursor(): Promise<boolean> {
  // Skip if cursor status already determined
  if (cursorEnabled !== null) return cursorEnabled;
  
  // Check settings
  const { cursorEnabled: settingEnabled } = useAppState.getState().settings;
  
  // Disable cursor if cursor is explicitly disabled
  if (!settingEnabled) {
    console.log('Cursor disabled in settings');
    cursorEnabled = false;
    return false;
  }
  
  try {
    // Try to inject cursor if it doesn't exist
    const cursorInjected = await executeScript(() => {
      // Check if cursor already exists
      if ((window as any).__superwizardCursor) {
        return true;
      }
      
      // Create a basic cursor implementation if none exists
      try {
        const cursor = {
          element: null as HTMLElement | null,
          isVisible: false,
          
          async moveTo(x: number, y: number): Promise<void> {
            return new Promise((resolve) => {
              // Create cursor element if it doesn't exist
              if (!this.element) {
                this.element = document.createElement('div');
                this.element.id = 'superwizard-cursor';
                this.element.style.cssText = `
                  position: fixed;
                  width: 20px;
                  height: 20px;
                  background: radial-gradient(circle, #ff6b6b 30%, rgba(255, 107, 107, 0.3) 70%);
                  border: 2px solid #ff6b6b;
                  border-radius: 50%;
                  pointer-events: none;
                  z-index: 10000;
                  transition: all 0.2s ease-out;
                  transform: translate(-50%, -50%);
                  box-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
                `;
                document.body.appendChild(this.element);
              }
              
              // Move cursor to position
              this.element.style.left = x + 'px';
              this.element.style.top = y + 'px';
              this.element.style.opacity = '1';
              this.isVisible = true;
              
              // Add a subtle animation
              this.element.style.transform = 'translate(-50%, -50%) scale(1.2)';
              setTimeout(() => {
                if (this.element) {
                  this.element.style.transform = 'translate(-50%, -50%) scale(1)';
                }
                resolve();
              }, 150);
            });
          },
          
          async click(): Promise<void> {
            return new Promise((resolve) => {
              if (!this.element || !this.isVisible) {
                resolve();
                return;
              }
              
              // Add click animation
              this.element.style.transform = 'translate(-50%, -50%) scale(0.8)';
              this.element.style.background = 'radial-gradient(circle, #ff4757 30%, rgba(255, 71, 87, 0.4) 70%)';
              
              setTimeout(() => {
                if (this.element) {
                  this.element.style.transform = 'translate(-50%, -50%) scale(1)';
                  this.element.style.background = 'radial-gradient(circle, #ff6b6b 30%, rgba(255, 107, 107, 0.3) 70%)';
                }
                resolve();
              }, 200);
            });
          },
          
          async simulateTyping(): Promise<void> {
            return new Promise((resolve) => {
              if (!this.element || !this.isVisible) {
                resolve();
                return;
              }
              
              // Add typing animation
              let pulseCount = 0;
              const pulseInterval = setInterval(() => {
                if (!this.element) {
                  clearInterval(pulseInterval);
                  resolve();
                  return;
                }
                
                if (pulseCount % 2 === 0) {
                  this.element.style.background = 'radial-gradient(circle, #5dade2 30%, rgba(93, 173, 226, 0.3) 70%)';
                  this.element.style.borderColor = '#5dade2';
                } else {
                  this.element.style.background = 'radial-gradient(circle, #ff6b6b 30%, rgba(255, 107, 107, 0.3) 70%)';
                  this.element.style.borderColor = '#ff6b6b';
                }
                
                pulseCount++;
                if (pulseCount >= 6) {
                  clearInterval(pulseInterval);
                  if (this.element) {
                    this.element.style.background = 'radial-gradient(circle, #ff6b6b 30%, rgba(255, 107, 107, 0.3) 70%)';
                    this.element.style.borderColor = '#ff6b6b';
                  }
                  resolve();
                }
              }, 200);
            });
          },
          
          hide(): void {
            if (this.element) {
              this.element.style.opacity = '0';
              this.isVisible = false;
              setTimeout(() => {
                if (this.element && this.element.parentNode) {
                  this.element.parentNode.removeChild(this.element);
                  this.element = null;
                }
              }, 300);
            }
          }
        };
        
        (window as any).__superwizardCursor = cursor;
        console.log('Superwizard cursor initialized successfully');
        return true;
      } catch (error) {
        console.error('Failed to create cursor implementation:', error);
        return false;
      }
    });
    
    if (cursorInjected) {
      cursorEnabled = true;
      console.log('Cursor initialization successful');
    } else {
      cursorEnabled = false;
      console.warn('Cursor injection failed');
    }
  } catch (error) {
    console.error('Error during cursor initialization:', error);
    cursorEnabled = false;
  }
  
  return cursorEnabled;
}

/**
 * Move cursor to specified coordinates
 */
export async function moveCursor(x: number, y: number, action?: 'click' | 'simulateTyping'): Promise<boolean> {
  try {
    if (!await initializeCursor()) {
      console.log('Cursor not available, skipping cursor movement');
      return false;
    }
    
    const result = await executeScript((x: number, y: number, action?: string) => {
      const cursor = (window as any).__superwizardCursor;
      if (!cursor) {
        console.warn('Cursor object not found in page context');
        return false;
      }
      
      return cursor.moveTo(x, y)
        .then(() => {
          if (action && typeof cursor[action] === 'function') {
            return cursor[action]();
          }
          return Promise.resolve();
        })
        .then(() => {
          console.log(`Cursor moved to (${x}, ${y})${action ? ` and performed ${action}` : ''}`);
          return true;
        })
        .catch((error: any) => {
          console.error('Cursor movement error:', error);
          return false;
        });
    }, x, y, action);
    
    return result || false;
  } catch (error) {
    console.error('Error in moveCursor:', error);
    return false;
  }
}

/**
 * Hide and cleanup cursor
 */
export async function hideCursor(): Promise<void> {
  try {
    if (cursorEnabled) {
      await executeScript(() => {
        const cursor = (window as any).__superwizardCursor;
        if (cursor && typeof cursor.hide === 'function') {
          cursor.hide();
          console.log('Cursor hidden and cleaned up');
        }
      });
    }
  } catch (error) {
    console.error('Error hiding cursor:', error);
  }
} 