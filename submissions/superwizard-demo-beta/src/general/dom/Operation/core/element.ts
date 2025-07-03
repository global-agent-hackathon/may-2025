/**
 * element.ts
 * 
 * Element discovery and access utilities for DOM operations
 */

import { useAppState } from '../../../../state/store';
import { callRPC } from '../../../browser/pageRPC';
import { NODE_ID_SELECTOR } from '../../../../constants';

/**
 * Execute a function in the context of the active tab
 */
export async function executeScript<T>(func: (...args: any[]) => T, ...args: any[]): Promise<T> {
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
 * Get element by its unique node ID
 */
export async function getElementByNodeId(elementId: number): Promise<{ uniqueId: string; element: any }> {
  try {
    const uniqueId = await callRPC('getUniqueElementSelectorId', [elementId]);
    
    if (!uniqueId) {
      throw new Error(`Failed to get unique element selector ID for element ${elementId}. The element may have been removed from the page or the RPC call failed.`);
    }
    
    const element = await executeScript((uniqueId: string, selector: string) => {
      const foundElement = document.querySelector(`[${selector}="${uniqueId}"]`);
      if (!foundElement) {
        // Provide debugging information
        const allElementsWithSelector = document.querySelectorAll(`[${selector}]`);
        return {
          element: null,
          debugInfo: {
            totalElementsWithSelector: allElementsWithSelector.length,
            existingIds: Array.from(allElementsWithSelector).slice(0, 5).map(el => el.getAttribute(selector)),
            documentReadyState: document.readyState,
            bodyChildCount: document.body ? document.body.children.length : 0
          }
        };
      }
      return { element: foundElement, debugInfo: null };
    }, uniqueId, NODE_ID_SELECTOR);
    
    if (!element || !element.element) {
      const debugInfo = element?.debugInfo;
      let errorMessage = `Element with ID ${elementId} not found in DOM using selector [${NODE_ID_SELECTOR}="${uniqueId}"].`;
      
      if (debugInfo) {
        errorMessage += ` Debug info: Document ready state: ${debugInfo.documentReadyState}, ` +
                       `Total elements with selector: ${debugInfo.totalElementsWithSelector}, ` +
                       `Body children: ${debugInfo.bodyChildCount}`;
        
        if (debugInfo.existingIds.length > 0) {
          errorMessage += `, Existing IDs: ${debugInfo.existingIds.join(', ')}`;
        } else {
          errorMessage += `, No elements found with the selector attribute`;
        }
      }
      
      throw new Error(errorMessage);
    }
    
    return { uniqueId, element: element.element };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    if (errorMessage.includes('not found in DOM')) {
      throw error; // Re-throw our detailed error
    }
    throw new Error(`Failed to get element by ID ${elementId}: ${errorMessage}. This could be due to network issues, page navigation, or the element being dynamically removed.`);
  }
}

/**
 * Get HTML element by its node ID
 */
export async function getHTMLElementById(elementId: number): Promise<HTMLElement> {
  const { uniqueId } = await getElementByNodeId(elementId);
  
  const element = await executeScript((uniqueId: string, selector: string) => {
    return document.querySelector(`[${selector}="${uniqueId}"]`) as HTMLElement;
  }, uniqueId, NODE_ID_SELECTOR);
  
  if (!element) {
    throw new Error('Could not find HTML element');
  }
  
  return element;
} 