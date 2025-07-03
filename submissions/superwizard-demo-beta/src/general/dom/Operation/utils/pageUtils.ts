/**
 * pageUtils.ts
 * 
 * Utility functions for page operations and helpers
 */

import { sleep } from '../../../utils/utils';

/**
 * Wait for a condition to be met with timeout
 */
export async function waitForCondition(
  conditionFn: () => boolean | Promise<boolean>,
  timeout: number = 5000,
  pollInterval: number = 100,
  description: string = 'condition'
): Promise<boolean> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    try {
      const result = await conditionFn();
      if (result) {
        return true;
      }
    } catch (error) {
      console.warn(`Error checking ${description}:`, error);
    }
    
    await sleep(pollInterval);
  }
  
  console.warn(`Timeout waiting for ${description} after ${timeout}ms`);
  return false;
}

/**
 * Retry a function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 100,
  multiplier: number = 2,
  description: string = 'operation'
): Promise<T> {
  let lastError: any;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      console.warn(`${description} attempt ${attempt + 1}/${maxRetries} failed:`, error);
      
      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(multiplier, attempt);
        await sleep(delay);
      }
    }
  }
  
  throw new Error(`${description} failed after ${maxRetries} attempts. Last error: ${lastError instanceof Error ? lastError.message : String(lastError)}`);
}

/**
 * Check if an element is in the viewport
 */
export function isElementInViewport(element: Element, margin: number = 0): boolean {
  const rect = element.getBoundingClientRect();
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
  
  return (
    rect.top >= -margin &&
    rect.left >= -margin &&
    rect.bottom <= viewportHeight + margin &&
    rect.right <= viewportWidth + margin
  );
}

/**
 * Get a safe element selector that can be used across page loads
 */
export function getSafeElementSelector(element: Element): string {
  // Build a selector path that's more resilient to page changes
  const path = [];
  let current: Element | null = element;
  
  while (current && current !== document.body) {
    let selector = current.tagName.toLowerCase();
    
    // Add ID if present and unique
    if (current.id) {
      const idSelector = `#${current.id}`;
      if (document.querySelectorAll(idSelector).length === 1) {
        path.unshift(idSelector);
        break; // ID is unique, we can stop here
      }
    }
    
    // Add classes if present
    if (current.classList.length > 0) {
      const classes = Array.from(current.classList)
        .filter(cls => !cls.match(/^(hover|active|focus|selected)$/)) // Skip state classes
        .slice(0, 2) // Limit to first 2 classes
        .join('.');
      if (classes) {
        selector += '.' + classes;
      }
    }
    
    // Add nth-child if there are siblings with same tag
    const siblings = current.parentElement?.children;
    if (siblings && siblings.length > 1) {
      const sameTagSiblings = Array.from(siblings).filter(s => s.tagName === current!.tagName);
      if (sameTagSiblings.length > 1) {
        const index = Array.from(siblings).indexOf(current) + 1;
        selector += `:nth-child(${index})`;
      }
    }
    
    path.unshift(selector);
    current = current.parentElement;
  }
  
  return path.join(' > ');
}

/**
 * Create a throttled version of a function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    } else {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = setTimeout(() => {
        lastCall = Date.now();
        func(...args);
      }, delay - (now - lastCall));
    }
  };
}

/**
 * Create a debounced version of a function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => func(...args), delay);
  };
} 