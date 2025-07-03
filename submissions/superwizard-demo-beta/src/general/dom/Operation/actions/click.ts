/**
 * click.ts
 * 
 * Click functionality for DOM operations
 */

import { sleep } from '../../../utils/utils';
import { CONFIG } from '../config';
import { ElementCoordinates, ClickResult } from '../types';
import { executeScript, getElementByNodeId } from '../core/element';
import { initializeCursor, moveCursor, hideCursor } from '../core/cursor';
import { getCenterCoordinates } from '../core/coordinates';
import { scrollIntoView } from './scroll';
import { NODE_ID_SELECTOR } from '../../../../constants';

/**
 * Click on an element
 */
export async function click(payload: { elementId: number }): Promise<void> {
  const elementId = payload.elementId;
  let operationContext = {
    scrollAttempted: false,
    scrollSuccess: false,
    scrollPartialSuccess: false,
    coordinatesObtained: false,
    coordinates: null as ElementCoordinates | null,
    cursorMoved: false,
    primaryClickAttempted: false,
    backupClickAttempted: false,
    lastError: null as string | null
  };

  try {
    // Try to initialize cursor
    await initializeCursor();
    
    let useBackupMethod = false;
    let scrollResult: { success: boolean; partialSuccess: boolean; reason?: string } | null = null;
    
    try {
      // First scroll the element into view
      operationContext.scrollAttempted = true;
      scrollResult = await scrollIntoView(elementId);
      operationContext.scrollSuccess = scrollResult.success;
      operationContext.scrollPartialSuccess = scrollResult.partialSuccess;
      
      // If scroll completely failed and made no progress, we might need backup approach
      if (!scrollResult.success && !scrollResult.partialSuccess) {
        console.warn('Scroll made no progress, but continuing with click attempt');
        operationContext.lastError = `Scroll failed: ${scrollResult.reason}`;
      }
      
      await sleep(CONFIG.CLICK.WAIT_AFTER_SCROLL);
      
      // Get coordinates with retries to ensure stability after scroll
      let stableCoordinates = false;
      let retryCount = 0;
      const MAX_COORDINATE_RETRIES = 3;
      const COORDINATE_STABILITY_THRESHOLD = 2;

      while (!stableCoordinates && retryCount < MAX_COORDINATE_RETRIES) {
        try {
          const newCoordinates = await getCenterCoordinates(elementId);
          operationContext.coordinatesObtained = true;
          
          if (!operationContext.coordinates) {
            operationContext.coordinates = newCoordinates;
          } else {
            // Check if coordinates are stable (haven't changed significantly)
            const isStable = Math.abs(operationContext.coordinates.x - newCoordinates.x) <= COORDINATE_STABILITY_THRESHOLD &&
                            Math.abs(operationContext.coordinates.y - newCoordinates.y) <= COORDINATE_STABILITY_THRESHOLD;
            
            if (isStable) {
              stableCoordinates = true;
              operationContext.coordinates = newCoordinates;
            } else {
              operationContext.coordinates = newCoordinates;
              await sleep(50); // Reduced wait before next check
            }
          }
        } catch (coordError) {
          console.warn(`Coordinate detection failed on attempt ${retryCount + 1}:`, coordError);
          operationContext.lastError = `Coordinate detection failed: ${coordError instanceof Error ? coordError.message : String(coordError)}`;
          // If we can't get coordinates but made some scroll progress, try backup method
          if (scrollResult?.partialSuccess) {
            break;
          }
        }
        
        retryCount++;
      }

      // Additional check to verify visibility at the computed coordinates (if we have them)
      if (operationContext.coordinates) {
        const isVisible = await executeScript((id: number, x: number, y: number) => {
          const element = document.querySelector(`[data-node-id="${id}"]`) as HTMLElement;
          if (!element) return false;
          
          // Check if element is actually at the computed coordinates
          const elementAtPoint = document.elementFromPoint(x, y);
          if (!elementAtPoint) return false;
          
          // Check if clicked element is the target or contains the target
          return element === elementAtPoint || element.contains(elementAtPoint) || elementAtPoint.contains(element);
        }, elementId, operationContext.coordinates.x, operationContext.coordinates.y);
        
        // If not visible at computed coordinates, but we had partial scroll success, continue anyway
        if (!isVisible && scrollResult?.partialSuccess) {
          console.warn('Element not visible at computed coordinates, but partial scroll succeeded - continuing');
          operationContext.lastError = 'Element not visible at computed coordinates after scroll';
        } else if (!isVisible) {
          console.warn('Element not visible at computed coordinates, attempting re-scroll');
          const reScrollResult = await scrollIntoView(elementId);
          await sleep(CONFIG.CLICK.WAIT_AFTER_SCROLL);
          
          // Get fresh coordinates after re-scroll
          try {
            operationContext.coordinates = await getCenterCoordinates(elementId);
          } catch (coordError) {
            console.warn('Failed to get coordinates after re-scroll:', coordError);
            operationContext.lastError = `Re-scroll coordinate detection failed: ${coordError instanceof Error ? coordError.message : String(coordError)}`;
            useBackupMethod = true;
          }
        }
      } else {
        // No coordinates available, but if we made scroll progress, try backup method
        if (scrollResult?.partialSuccess) {
          console.warn('No coordinates available but scroll made progress - using backup method');
          useBackupMethod = true;
        }
      }
    } catch (scrollError) {
      console.warn('Scroll or coordinate detection failed:', scrollError);
      operationContext.lastError = `Scroll/coordinate phase failed: ${scrollError instanceof Error ? scrollError.message : String(scrollError)}`;
      useBackupMethod = true;
    }

    // If we have coordinates and haven't encountered issues, try primary click method
    if (operationContext.coordinates && !useBackupMethod) {
      try {
        operationContext.primaryClickAttempted = true;
        
        // Try to use cursor simulation if enabled
        const cursorMoved = await moveCursor(operationContext.coordinates.x, operationContext.coordinates.y, 'click');
        operationContext.cursorMoved = cursorMoved;
        
        // If cursor was used, wait for animation
        if (cursorMoved) {
          await sleep(CONFIG.CLICK.WAIT_AFTER_CLICK);
        }
        
        // Perform the click using standard DOM events
        const clickSuccess = await executeScript((x: number, y: number) => {
          const element = document.elementFromPoint(x, y);
          if (!element) return false;
          
          const eventOptions = {
            bubbles: true,
            cancelable: true,
            view: window,
            clientX: x,
            clientY: y,
            detail: 1
          };
          
          // Dispatch all relevant mouse events in sequence
          element.dispatchEvent(new MouseEvent('mousedown', eventOptions));
          element.dispatchEvent(new MouseEvent('click', eventOptions));
          element.dispatchEvent(new MouseEvent('mouseup', eventOptions));
          
          return true;
        }, operationContext.coordinates.x, operationContext.coordinates.y);
        
        if (!clickSuccess) {
          throw new Error('No element found at the specified coordinates');
        }
        
        await sleep(CONFIG.CLICK.WAIT_AFTER_CLICK);
        
        // Hide cursor after successful primary click
        await hideCursor();
        
        return; // If successful, return early
      } catch (clickError) {
        console.warn('Primary click method failed:', clickError);
        operationContext.lastError = `Primary click failed: ${clickError instanceof Error ? clickError.message : String(clickError)}`;
        useBackupMethod = true;
      }
    }

    // Backup click method - used when scroll fails, coordinates fail, or primary click fails
    console.warn('Using backup click method');
    operationContext.backupClickAttempted = true;
    
    // Add a small delay to allow any animations or state changes to complete
    await sleep(50);
    
    // Get element reference for backup method
    let uniqueId: string;
    try {
      const elementRef = await getElementByNodeId(elementId);
      uniqueId = elementRef.uniqueId;
    } catch (elementError) {
      operationContext.lastError = `Element lookup failed in backup method: ${elementError instanceof Error ? elementError.message : String(elementError)}`;
      throw new Error(buildClickErrorMessage(elementId, operationContext));
    }
    
    // Execute backup click operation in the context of the page
    const clickResult = await executeScript<ClickResult>((uniqueId: string, selector: string) => {
      const element = document.querySelector(`[${selector}="${uniqueId}"]`);
      if (!element) return { success: false, reason: 'Element not found' };
      
      try {
        // Special handling for dropdown/combobox/select elements
        const role = element.getAttribute('role');
        const tagName = element.tagName.toLowerCase();
        const ariaLabel = element.getAttribute('aria-label');
        
        // Check if this is a dropdown option or combobox element
        if (role === 'option' || tagName === 'option' || 
            (role === 'combobox' && element.getAttribute('aria-expanded')) ||
            ariaLabel?.includes('option:')) {
          
          // Method 1: Handle select dropdown options
          if (tagName === 'option' && element.parentElement?.tagName.toLowerCase() === 'select') {
            const select = element.parentElement as HTMLSelectElement;
            const option = element as HTMLOptionElement;
            option.selected = true;
            select.value = option.value;
            
            // Dispatch change events
            select.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
            select.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
            return { success: true, method: 'select-option' };
          }
          
          // Method 2: Handle ARIA combobox pattern
          if (role === 'option') {
            // Look for parent combobox or listbox
            const combobox = element.closest('[role="combobox"]') || 
                           document.querySelector('[aria-controls][aria-expanded="true"]');
            
            if (combobox) {
              // Set the value if it's an input
              if (combobox.tagName.toLowerCase() === 'input') {
                (combobox as HTMLInputElement).value = element.textContent?.trim() || '';
                combobox.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
                combobox.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
              }
              
              // Set aria-selected on the option
              element.setAttribute('aria-selected', 'true');
              
              // Remove aria-selected from siblings
              const siblings = element.parentElement?.querySelectorAll('[role="option"]');
              siblings?.forEach(sibling => {
                if (sibling !== element) {
                  sibling.setAttribute('aria-selected', 'false');
                }
              });
              
              // Close the dropdown
              combobox.setAttribute('aria-expanded', 'false');
            }
            
            // Always try clicking the option as well
            (element as HTMLElement).click();
            return { success: true, method: 'aria-option' };
          }
          
          // Method 3: Handle custom dropdown patterns
          if (role === 'combobox' || element.getAttribute('aria-haspopup')) {
            // If this is the combobox trigger, we need to find and click the specific option
            const listboxId = element.getAttribute('aria-controls');
            const expanded = element.getAttribute('aria-expanded') === 'true';
            
            if (!expanded) {
              // First open the dropdown
              (element as HTMLElement).click();
              return { success: true, method: 'combobox-open' };
            }
          }
        }
        
        // Try multiple click methods in sequence for maximum compatibility
        
        // Method 1: Native click() for standard elements
        if (element instanceof HTMLElement) {
          element.click();
          return { success: true, method: 'native' };
        }
        
        // Method 2: Dispatch click event
        const clickEvent = new MouseEvent('click', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        element.dispatchEvent(clickEvent);
        
        // Method 3: Try mousedown + mouseup sequence (more realistic)
        const mouseDownEvent = new MouseEvent('mousedown', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        const mouseUpEvent = new MouseEvent('mouseup', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        element.dispatchEvent(mouseDownEvent);
        element.dispatchEvent(mouseUpEvent);
        
        // Method 4: Try jQuery click if available
        if ((window as any).jQuery && (window as any).jQuery(element).trigger) {
          (window as any).jQuery(element).trigger('click');
        }
        
        // Method 5: Try invoking onclick handler directly
        if (typeof (element as any).onclick === 'function') {
          (element as any).onclick();
        }
        
        return { success: true, method: 'fallback' };
      } catch (error) {
        return { 
          success: false, 
          reason: error instanceof Error ? error.message : String(error),
          method: 'failed'
        };
      }
    }, uniqueId, NODE_ID_SELECTOR);
    
    if (!clickResult.success) {
      operationContext.lastError = `Backup click method failed: ${clickResult.reason}`;
      throw new Error(buildClickErrorMessage(elementId, operationContext));
    }
    
    await sleep(CONFIG.CLICK.WAIT_AFTER_CLICK);
    
    // Hide cursor after successful click
    await hideCursor();
    
  } catch (error: any) {
    // Hide cursor on error as well
    await hideCursor();
    
    // If it's already our detailed error, re-throw it
    if (error.message && error.message.includes('Click operation failed for element')) {
      throw error;
    }
    
    // Otherwise, build a detailed error message
    operationContext.lastError = error.message || String(error);
    throw new Error(buildClickErrorMessage(elementId, operationContext));
  }
}

/**
 * Build a detailed error message for click failures
 */
function buildClickErrorMessage(elementId: number, context: any): string {
  let message = `Click operation failed for element ${elementId}. `;
  
  // Add scroll information
  if (context.scrollAttempted) {
    if (context.scrollSuccess) {
      message += 'Scroll: ✓ Successful. ';
    } else if (context.scrollPartialSuccess) {
      message += 'Scroll: ⚠ Partially successful. ';
    } else {
      message += 'Scroll: ✗ Failed. ';
    }
  } else {
    message += 'Scroll: Not attempted. ';
  }
  
  // Add coordinate information
  if (context.coordinatesObtained) {
    message += `Coordinates: ✓ Obtained (${context.coordinates?.x}, ${context.coordinates?.y}). `;
  } else {
    message += 'Coordinates: ✗ Failed to obtain. ';
  }
  
  // Add cursor information
  if (context.cursorMoved) {
    message += 'Cursor: ✓ Moved. ';
  } else {
    message += 'Cursor: ✗ Not moved. ';
  }
  
  // Add click method information
  if (context.primaryClickAttempted && context.backupClickAttempted) {
    message += 'Methods: Both primary and backup failed. ';
  } else if (context.primaryClickAttempted) {
    message += 'Methods: Primary failed, backup not attempted. ';
  } else if (context.backupClickAttempted) {
    message += 'Methods: Primary skipped, backup failed. ';
  } else {
    message += 'Methods: Neither primary nor backup attempted. ';
  }
  
  // Add the last error
  if (context.lastError) {
    message += `Last error: ${context.lastError}`;
  }
  
  return message;
} 