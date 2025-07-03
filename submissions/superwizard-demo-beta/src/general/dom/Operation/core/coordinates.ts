/**
 * coordinates.ts
 * 
 * Coordinate calculation utilities for DOM operations
 */

import { sleep } from '../../../utils/utils';
import { CONFIG } from '../config';
import { ElementCoordinates } from '../types';
import { executeScript, getElementByNodeId } from './element';
import { NODE_ID_SELECTOR } from '../../../../constants';

/**
 * Get the center coordinates of an element
 */
export async function getCenterCoordinates(elementId: number): Promise<ElementCoordinates> {
  const { MAX_RETRIES, RETRY_DELAY, VIEWPORT_MARGIN, MAX_COORDINATE_VALUE } = CONFIG.COORDINATES;
  
  let lastError = '';
  let lastRect: any = null;
  let elementFound = false;
  
  for (let attempts = 0; attempts < MAX_RETRIES; attempts++) {
    try {
      const { uniqueId } = await getElementByNodeId(elementId);
      
      const coordinates = await executeScript((uniqueId: string, selector: string, margin: number) => {
        const element = document.querySelector(`[${selector}="${uniqueId}"]`);
        if (!element) {
          return { 
            error: 'Element not found in DOM',
            elementExists: false,
            selector: `[${selector}="${uniqueId}"]`
          };
        }
        
        const rect = element.getBoundingClientRect();
        
        if (rect.width <= 0 || rect.height <= 0) {
          return { 
            error: 'Element has no dimensions',
            elementExists: true,
            rect: {
              top: rect.top,
              right: rect.right,
              bottom: rect.bottom,
              left: rect.left,
              width: rect.width,
              height: rect.height
            },
            computedStyle: {
              display: window.getComputedStyle(element).display,
              visibility: window.getComputedStyle(element).visibility,
              opacity: window.getComputedStyle(element).opacity
            }
          };
        }
        
        const inViewport = 
          rect.bottom > -margin && 
          rect.right > -margin && 
          rect.top < window.innerHeight + margin && 
          rect.left < window.innerWidth + margin;
          
        return {
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2,
          isVisible: inViewport,
          rect: {
            top: rect.top,
            right: rect.right,
            bottom: rect.bottom,
            left: rect.left,
            width: rect.width,
            height: rect.height
          },
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight
          },
          elementExists: true
        };
      }, uniqueId, NODE_ID_SELECTOR, VIEWPORT_MARGIN);
      
      // Check for errors returned from the script
      if (coordinates && 'error' in coordinates) {
        elementFound = coordinates.elementExists;
        lastRect = coordinates.rect || null;
        lastError = coordinates.error || '';
        
        if (attempts === MAX_RETRIES - 1) {
          let errorMessage = `Failed to get coordinates for element ${elementId}: ${coordinates.error || ''}. `;
          if (!coordinates.elementExists) {
            errorMessage += `Element not found using selector [${NODE_ID_SELECTOR}="${uniqueId}"]. `;
          } else if (coordinates.rect) {
            errorMessage += `Element found but has dimensions ${coordinates.rect.width}x${coordinates.rect.height} at position (${coordinates.rect.left}, ${coordinates.rect.top}). `;
            
            if (coordinates.computedStyle) {
              errorMessage += `Computed styles: display="${coordinates.computedStyle.display}", visibility="${coordinates.computedStyle.visibility}", opacity="${coordinates.computedStyle.opacity}". `;
            }
          }
          
          throw new Error(errorMessage);
        }
        
        await sleep(RETRY_DELAY * (attempts + 1));
        continue;
      }
      
      // Element not found or has no dimensions
      if (!coordinates) {
        lastError = 'Script returned null coordinates';
        if (attempts === MAX_RETRIES - 1) {
          throw new Error(`Failed to get coordinates for element ${elementId}: Script execution returned null. Element may have been removed or script context lost.`);
        }
        await sleep(RETRY_DELAY * (attempts + 1));
        continue;
      }
      
      // Element found but not in viewport, try to scroll it into view
      if (!coordinates.isVisible) {
        lastRect = coordinates.rect;
        lastError = `Element not in viewport (position: ${coordinates.rect.left}, ${coordinates.rect.top}, size: ${coordinates.rect.width}x${coordinates.rect.height}, viewport: ${coordinates.viewport.width}x${coordinates.viewport.height})`;
        
        await executeScript((uniqueId: string, selector: string) => {
          const element = document.querySelector(`[${selector}="${uniqueId}"]`);
          if (!element) return false;
          element.scrollIntoView({ behavior: 'auto', block: 'center' });
          return true;
        }, uniqueId, NODE_ID_SELECTOR);
        
        await sleep(RETRY_DELAY);
        continue;
      }
      
      // Validate coordinates are reasonable values
      if (isNaN(coordinates.x) || isNaN(coordinates.y) || 
          coordinates.x < 0 || coordinates.y < 0 || 
          coordinates.x > MAX_COORDINATE_VALUE || coordinates.y > MAX_COORDINATE_VALUE) {
        lastError = `Invalid coordinates computed: (${coordinates.x}, ${coordinates.y})`;
        lastRect = coordinates.rect;
        
        if (attempts === MAX_RETRIES - 1) {
          throw new Error(`Failed to get coordinates for element ${elementId}: Computed invalid coordinates (${coordinates.x}, ${coordinates.y}). Element rect: ${JSON.stringify(coordinates.rect)}, viewport: ${JSON.stringify(coordinates.viewport)}`);
        }
        await sleep(RETRY_DELAY * (attempts + 1));
        continue;
      }
      
      return { x: coordinates.x, y: coordinates.y };
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
      
      if (attempts === MAX_RETRIES - 1) {
        let errorMessage = `Failed to get coordinates for element ${elementId} after ${MAX_RETRIES} attempts. `;
        
        if (lastRect) {
          errorMessage += `Last known element position: (${lastRect.left}, ${lastRect.top}), size: ${lastRect.width}x${lastRect.height}. `;
        }
        
        if (elementFound) {
          errorMessage += 'Element was found but could not determine valid coordinates. ';
        } else {
          errorMessage += 'Element was not found in DOM. ';
        }
        
        errorMessage += `Last error: ${lastError}`;
        
        throw new Error(errorMessage);
      }
      await sleep(RETRY_DELAY * (attempts + 1));
    }
  }
  
  throw new Error(`Failed to get element coordinates for element ${elementId} after multiple attempts. Last error: ${lastError}`);
} 