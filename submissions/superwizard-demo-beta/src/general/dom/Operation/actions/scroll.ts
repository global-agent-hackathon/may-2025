/**
 * scroll.ts
 * 
 * Scrolling functionality for DOM operations
 */

import { sleep } from '../../../utils/utils';
import { CONFIG } from '../config';
import { ScrollResult } from '../types';
import { executeScript, getElementByNodeId } from '../core/element';
import { useAppState } from '../../../../state/store';
import { NODE_ID_SELECTOR } from '../../../../constants';

/**
 * Scroll an element into view with enhanced reliability and better fallback handling
 */
export async function scrollIntoView(elementId: number, smooth: boolean = true): Promise<{ success: boolean; partialSuccess: boolean; reason?: string }> {
  const { MAX_RETRIES, RETRY_DELAY_BASE, VISIBLE_WAIT_TIME, MIN_SMOOTH_TIMEOUT, MAX_SMOOTH_TIMEOUT, VIEWPORT_TOLERANCE } = CONFIG.SCROLL;
  const WAIT_TIME = 300;  // Always use smooth scroll timing
  
  let bestResult: ScrollResult | null = null;
  let anyProgressMade = false;
  
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const { uniqueId } = await getElementByNodeId(elementId);
      
      const scrollResult = await executeScript<Promise<ScrollResult>>((uniqueId: string, selector: string, tolerance: number, minTimeout: number, maxTimeout: number) => {
        const element = document.querySelector(`[${selector}="${uniqueId}"]`);
        if (!element) return Promise.resolve({ success: false, reason: 'Element not found' });
        
        // Get initial position
        const initialRect = element.getBoundingClientRect();
        
        // Check if element has dimensions
        if (initialRect.width <= 0 || initialRect.height <= 0) {
          return Promise.resolve({ 
            success: false, 
            reason: 'Element has no dimensions',
            position: { 
              x: initialRect.left, 
              y: initialRect.top, 
              width: initialRect.width, 
              height: initialRect.height 
            }
          });
        }
        
        // Check if element is already reasonably visible - more lenient criteria
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        const isAlreadyVisible = 
          initialRect.top >= -(tolerance * 2) && 
          initialRect.left >= -(tolerance * 2) && 
          initialRect.bottom <= viewportHeight + (tolerance * 2) && 
          initialRect.right <= viewportWidth + (tolerance * 2);
          
        if (isAlreadyVisible) {
          return Promise.resolve({
            success: true,
            reason: 'Already visible',
            position: {
              x: initialRect.left,
              y: initialRect.top,
              width: initialRect.width,
              height: initialRect.height
            },
            isFullyVisible: true,
            isPartiallyVisible: true,
            madeProgress: false
          });
        }
        
        // Calculate dynamic timeout based on scroll distance (more aggressive)
        const scrollDistance = Math.abs(initialRect.top - viewportHeight / 2) + Math.abs(initialRect.left - viewportWidth / 2);
        const dynamicTimeout = Math.min(maxTimeout, Math.max(minTimeout, scrollDistance / 4));  // Divided by 4 instead of 2 for faster timeout
        
        // Try multiple scroll methods with enhanced fallbacks and nested container handling - always smooth
        let scrollAttempted = false;
        
        try {
          // Method 1: Check if element is inside a scrollable container first
          let scrollableParent = element.parentElement;
          let foundScrollableParent = false;
          
          while (scrollableParent && scrollableParent !== document.body) {
            const parentStyle = getComputedStyle(scrollableParent);
            const isScrollable = parentStyle.overflow === 'auto' || 
                               parentStyle.overflow === 'scroll' || 
                               parentStyle.overflowY === 'auto' || 
                               parentStyle.overflowY === 'scroll' ||
                               parentStyle.overflowX === 'auto' || 
                               parentStyle.overflowX === 'scroll';
            
            if (isScrollable && scrollableParent.scrollHeight > scrollableParent.clientHeight) {
              try {
                // Scroll within the container first - always smooth
                const elementTop = (element as HTMLElement).offsetTop;
                const containerTop = (scrollableParent as HTMLElement).offsetTop;
                const relativeTop = elementTop - containerTop;
                const targetScroll = relativeTop - (scrollableParent.clientHeight / 2);
                
                scrollableParent.scrollTo({
                  top: Math.max(0, targetScroll),
                  behavior: 'smooth'
                });
                foundScrollableParent = true;
                scrollAttempted = true;
                break;
              } catch (e) {
                // Continue searching for other scrollable parents
              }
            }
            scrollableParent = scrollableParent.parentElement;
          }
          
          // Method 2: Native scrollIntoView with smooth behavior
          if (!foundScrollableParent) {
            element.scrollIntoView({ 
              behavior: 'smooth',
              block: 'center',
              inline: 'center'
            });
            scrollAttempted = true;
          }
        } catch (e) {
          try {
            // Method 3: Try with 'nearest' block option - smooth
            element.scrollIntoView({ 
              behavior: 'smooth',
              block: 'nearest',
              inline: 'nearest'
            });
            scrollAttempted = true;
          } catch (e2) {
            // Method 4: Fallback to window.scroll - smooth
            try {
              const rect = element.getBoundingClientRect();
              const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
              const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
              const targetY = scrollTop + rect.top - (viewportHeight / 2) + (rect.height / 2);
              const targetX = scrollLeft + rect.left - (viewportWidth / 2) + (rect.width / 2);
              
              window.scroll({
                top: Math.max(0, targetY),
                left: Math.max(0, targetX),
                behavior: 'smooth'
              });
              scrollAttempted = true;
            } catch (e3) {
              // Method 5: Direct scrollTo as last resort - smooth
              try {
                window.scrollTo({
                  top: window.pageYOffset + initialRect.top - viewportHeight / 2,
                  behavior: 'smooth'
                });
                scrollAttempted = true;
              } catch (e4) {
                // All methods failed
              }
            }
          }
        }
        
        if (!scrollAttempted) {
          return Promise.resolve({ success: false, reason: 'No scroll method succeeded' });
        }
        
        // Verify scroll was successful with enhanced criteria
        return new Promise(resolve => {
          setTimeout(() => {
            const newRect = element.getBoundingClientRect();
            
            // Much more lenient visibility checks
            const expandedTolerance = tolerance * 3; // Triple the tolerance
            const isFullyVisible = 
              newRect.top >= -expandedTolerance && 
              newRect.left >= -expandedTolerance && 
              newRect.bottom <= viewportHeight + expandedTolerance && 
              newRect.right <= viewportWidth + expandedTolerance;
            
            const isPartiallyVisible =
              newRect.top < viewportHeight + expandedTolerance &&
              newRect.bottom > -expandedTolerance &&
              newRect.left < viewportWidth + expandedTolerance &&
              newRect.right > -expandedTolerance;
            
            // Check if scroll made any progress at all
            const madeProgress = 
              Math.abs(newRect.top - initialRect.top) > 5 ||
              Math.abs(newRect.left - initialRect.left) > 5;
            
            // Much more lenient success criteria - accept partial visibility or any progress
            const isAcceptablyVisible = isPartiallyVisible && (
              // Element center is somewhere near viewport
              (newRect.left + newRect.width / 2 >= -expandedTolerance && 
               newRect.left + newRect.width / 2 <= viewportWidth + expandedTolerance &&
               newRect.top + newRect.height / 2 >= -expandedTolerance && 
               newRect.top + newRect.height / 2 <= viewportHeight + expandedTolerance) ||
              // At least 10% of element is visible (reduced from 25%)
              (Math.max(0, Math.min(newRect.right, viewportWidth) - Math.max(newRect.left, 0)) *
               Math.max(0, Math.min(newRect.bottom, viewportHeight) - Math.max(newRect.top, 0))) >= 
               (newRect.width * newRect.height * 0.1) ||
              // Or significant progress was made toward visibility
              madeProgress
            );
            
            resolve({
              success: isFullyVisible || isAcceptablyVisible,
              position: {
                x: newRect.left,
                y: newRect.top,
                width: newRect.width,
                height: newRect.height
              },
              isFullyVisible,
              isPartiallyVisible,
              madeProgress,
              reason: isFullyVisible ? 'Fully visible' : 
                      isAcceptablyVisible ? 'Acceptably visible' : 
                      madeProgress ? 'Made progress but not visible' : 
                      'Still not visible'
            });
          }, dynamicTimeout);
        });
      }, uniqueId, NODE_ID_SELECTOR, VIEWPORT_TOLERANCE, MIN_SMOOTH_TIMEOUT, MAX_SMOOTH_TIMEOUT);
      
      // Store the best result we've achieved
      if (scrollResult && typeof scrollResult === 'object' && 'success' in scrollResult) {
        if (!bestResult || scrollResult.success || scrollResult.madeProgress) {
          bestResult = scrollResult as ScrollResult;
        }
        
        if (scrollResult.madeProgress) {
          anyProgressMade = true;
        }
        
        // If we achieved success, return immediately
        if (scrollResult.success) {
          await sleep(WAIT_TIME);
          return { success: true, partialSuccess: true };
        }
      }
      
      // Log detailed scroll attempt information
      console.warn(
        `Scroll attempt ${attempt + 1}/${MAX_RETRIES} - partial result:`,
        scrollResult && typeof scrollResult === 'object' ? {
          reason: (scrollResult as ScrollResult).reason || 'Unknown reason',
          position: (scrollResult as ScrollResult).position || {},
          isFullyVisible: (scrollResult as ScrollResult).isFullyVisible,
          isPartiallyVisible: (scrollResult as ScrollResult).isPartiallyVisible,
          madeProgress: (scrollResult as ScrollResult).madeProgress
        } : 'Unknown result'
      );
      
      // Progressive retry delay
      const retryDelay = RETRY_DELAY_BASE * Math.pow(1.2, attempt);  // Reduced from 1.5x to 1.2x
      await sleep(retryDelay);
    } catch (error) {
      console.error(`Scroll error on attempt ${attempt + 1}/${MAX_RETRIES}:`, error);
      
      if (attempt === MAX_RETRIES - 1) {
        // Before final failure, try one last desperate attempt with smooth scroll
        try {
          const { uniqueId } = await getElementByNodeId(elementId);
          const lastResortResult = await executeScript((uniqueId: string, selector: string) => {
            const element = document.querySelector(`[${selector}="${uniqueId}"]`);
            if (!element) return false;
            
            // Force smooth scroll to element
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Also try to focus the element to ensure it's interactable
            if (element instanceof HTMLElement && typeof element.focus === 'function') {
              try {
                element.focus();
              } catch (e) {
                // Focus might fail, but scroll might have worked
              }
            }
            
            // Check if element is now at least partially visible - very lenient check
            const rect = element.getBoundingClientRect();
            return rect.top < window.innerHeight + 100 && rect.bottom > -100 && 
                   rect.left < window.innerWidth + 100 && rect.right > -100;
          }, uniqueId, NODE_ID_SELECTOR);
          
          if (lastResortResult) {
            console.log('Last resort scroll attempt succeeded');
            await sleep(WAIT_TIME);
            return { success: true, partialSuccess: true };
          }
        } catch (lastResortError) {
          console.error('Last resort scroll also failed:', lastResortError);
        }
      }
      
      await sleep(RETRY_DELAY_BASE * Math.pow(1.2, attempt));  // Reduced multiplier for faster retries
    }
  }
  
  // If we made any progress or achieved partial visibility, consider it a partial success
  const partialSuccess = anyProgressMade || (bestResult && (bestResult.isPartiallyVisible || bestResult.madeProgress));
  
  console.warn('Scroll attempts completed with limited success:', {
    anyProgressMade,
    bestResult: bestResult ? {
      isPartiallyVisible: bestResult.isPartiallyVisible,
      madeProgress: bestResult.madeProgress,
      reason: bestResult.reason
    } : 'No result'
  });
  
  return { 
    success: false, 
    partialSuccess: !!partialSuccess,
    reason: bestResult?.reason || 'Failed to scroll element into view after all attempts'
  };
} 