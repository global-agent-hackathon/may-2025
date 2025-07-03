/**
 * stability.ts
 * 
 * Page stability and readiness checking for DOM operations
 */

import { CONFIG } from '../config';

/**
 * Cache for page stability to avoid redundant checks
 */
let lastStabilityCheck = 0;
let lastStabilityResult = true;

/**
 * Enhanced page loading and stability check
 */
async function checkPageLoadingAndStability(tabId: number): Promise<void> {
  const { TIMEOUT, POLL_INTERVAL, CONSISTENT_CHECKS_REQUIRED, MIN_STABLE_TIME, MAX_MUTATION_COUNT } = CONFIG.PAGE_STABILITY;
  
  return new Promise((resolve) => {
    let startTime = Date.now();
    let lastStableTime = 0;
    let consistentStableChecks = 0;
    let lastStabilityResult: any = null;
    
    const checkStability = async () => {
      try {
        const domSnapshot = await chrome.scripting.executeScript({
          target: { tabId },
          func: (maxMutations: number) => {
            // 1. Document readiness check
            if (document.readyState !== 'complete') {
              return { isStable: false, reason: 'document-not-ready', details: { readyState: document.readyState } };
            }

            // 2. Check for pending network requests
            const pendingFetchCount = (window as any).__superwizard_pending_fetch_count || 0;
            if (pendingFetchCount > 0) {
              return { isStable: false, reason: 'pending-fetch-requests', details: { count: pendingFetchCount } };
            }

            const pendingXHRCount = (window as any).__superwizard_pending_xhr_count || 0;
            if (pendingXHRCount > 0) {
              return { isStable: false, reason: 'pending-xhr-requests', details: { count: pendingXHRCount } };
            }

            // 3. Check for loading resources (images, scripts, stylesheets)
            const loadingImages = Array.from(document.querySelectorAll('img')).filter(img => !img.complete);
            if (loadingImages.length > 0) {
              return { isStable: false, reason: 'images-loading', details: { count: loadingImages.length } };
            }

            const loadingStylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).filter(link => {
              try {
                return !(link as HTMLLinkElement).sheet || (link as HTMLLinkElement).sheet!.cssRules.length === 0;
              } catch {
                return true; // Assume loading if we can't access cssRules
              }
            });
            if (loadingStylesheets.length > 0) {
              return { isStable: false, reason: 'stylesheets-loading', details: { count: loadingStylesheets.length } };
            }

            // 4. Check for common loading indicators
            const loadingIndicators = document.querySelectorAll(`
              [aria-busy="true"],
              .loading, .loader, .spinner, .spinning,
              [class*="loading"], [class*="spinner"], [class*="loading-"],
              [data-loading="true"], [data-testid*="loading"],
              .skeleton, [class*="skeleton"],
              .progress, [class*="progress"]
            `);
            if (loadingIndicators.length > 0) {
              return { isStable: false, reason: 'loading-indicators', details: { count: loadingIndicators.length } };
            }

            // 5. Check mutation count (DOM changes)
            const mutationCount = (window as any).__superwizard_mutation_count || 0;
            if (mutationCount > maxMutations) {
              return { isStable: false, reason: 'high-mutation-count', details: { count: mutationCount, max: maxMutations } };
            }

            // 6. Check for JavaScript framework loading states
            if (typeof (window as any).React !== 'undefined') {
              const reactLoadingElements = document.querySelectorAll('[data-react-loading="true"], [data-loading-state="true"]');
              if (reactLoadingElements.length > 0) {
                return { isStable: false, reason: 'react-loading-state', details: { count: reactLoadingElements.length } };
              }
            }

            if (typeof (window as any).Vue !== 'undefined') {
              const vueLoadingElements = document.querySelectorAll('[v-loading="true"], .v-loading');
              if (vueLoadingElements.length > 0) {
                return { isStable: false, reason: 'vue-loading-state', details: { count: vueLoadingElements.length } };
              }
            }

            // 7. Check for dynamic content containers that might still be loading
            const emptyContainers = document.querySelectorAll(`
              main:empty, .content:empty, .main-content:empty,
              [role="main"]:empty, [data-testid="content"]:empty,
              .page-content:empty, #content:empty
            `);
            if (emptyContainers.length > 0) {
              return { isStable: false, reason: 'empty-content-containers', details: { count: emptyContainers.length } };
            }

            // 8. Check for pending timers that might affect content
            const pendingTimerCount = (window as any).__superwizard_pending_timer_count || 0;
            if (pendingTimerCount > 2) { // Allow some timers for normal operations
              return { isStable: false, reason: 'many-pending-timers', details: { count: pendingTimerCount } };
            }

            return { 
              isStable: true, 
              details: { 
                readyState: document.readyState,
                mutationCount,
                loadingIndicators: 0,
                pendingRequests: 0
              }
            };
          },
          args: [MAX_MUTATION_COUNT]
        });

        if (!domSnapshot || !domSnapshot[0]?.result) {
          throw new Error('Failed to get DOM snapshot');
        }

        const result = domSnapshot[0].result;
        const currentTime = Date.now();
        
        if (result.isStable) {
          if (lastStabilityResult?.isStable) {
            consistentStableChecks++;
          } else {
            consistentStableChecks = 1;
            lastStableTime = currentTime;
          }
          
          if (consistentStableChecks >= CONSISTENT_CHECKS_REQUIRED && 
              (currentTime - lastStableTime) >= MIN_STABLE_TIME) {
            console.log('Page stability achieved:', result.details);
            resolve();
            return;
          }
        } else {
          consistentStableChecks = 0;
          console.log('Page not stable:', result.reason, result.details);
        }
        
        lastStabilityResult = result;

        if (currentTime - startTime > TIMEOUT) {
          console.warn('Page stability timeout exceeded:', result.reason, result.details);
          resolve();
          return;
        }

        setTimeout(checkStability, POLL_INTERVAL);
      } catch (error) {
        console.error('Error checking page stability:', error);
        setTimeout(checkStability, POLL_INTERVAL);
      }
    };
    
    checkStability();
  });
}

/**
 * Enhanced page stability check that includes comprehensive loading and mutation monitoring
 */
export async function ensurePageStability(tabId: number): Promise<void> {
  const { SKIP_STABILITY_THRESHOLD } = CONFIG.PAGE_STABILITY;
  const now = Date.now();
  
  // Skip stability check if we checked recently and it was stable
  if (lastStabilityResult && (now - lastStabilityCheck) < SKIP_STABILITY_THRESHOLD) {
    return;
  }
  
  // Set up comprehensive monitoring (mutation observer + network monitoring)
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      func: () => {
        // Set up mutation observer
        if (!(window as any).__superwizard_mutation_observer) {
          let mutationCount = 0;
          let resetTimer: ReturnType<typeof setTimeout>;
          
          const observer = new MutationObserver((mutations) => {
            const significantMutations = mutations.filter(m => {
              if (m.type === 'attributes' && m.attributeName === 'style') return false;
              if (m.type === 'attributes' && m.attributeName === 'class') {
                const target = m.target as HTMLElement;
                return window.getComputedStyle(target).display !== 'none';
              }
              return true;
            });

            if (significantMutations.length > 0) {
              mutationCount++;
              (window as any).__superwizard_mutation_count = mutationCount;
              
              clearTimeout(resetTimer);
              resetTimer = setTimeout(() => {
                mutationCount = Math.max(0, mutationCount - 1);
                (window as any).__superwizard_mutation_count = mutationCount;
              }, 100);
            }
          });
          
          observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            characterData: false,
            attributeFilter: ['class', 'style', 'aria-busy', 'hidden', 'data-loading', 'data-loading-state'],
          });
          
          (window as any).__superwizard_mutation_observer = observer;
        }

        // Set up network request monitoring
        if (!(window as any).__superwizard_network_monitor) {
          (window as any).__superwizard_pending_fetch_count = 0;
          (window as any).__superwizard_pending_xhr_count = 0;
          (window as any).__superwizard_pending_timer_count = 0;
          
          // Monitor fetch requests
          const originalFetch = window.fetch;
          (window as any).fetch = async function(...args: Parameters<typeof fetch>) {
            (window as any).__superwizard_pending_fetch_count++;
            try {
              const result = await originalFetch.apply(this, args);
              return result;
            } finally {
              (window as any).__superwizard_pending_fetch_count = Math.max(0, (window as any).__superwizard_pending_fetch_count - 1);
            }
          };

          // Monitor XMLHttpRequest
          const XHRProto = XMLHttpRequest.prototype;
          const originalOpen = XHRProto.open;
          
          XHRProto.open = function(method: string, url: string | URL, async: boolean = true, username?: string | null, password?: string | null) {
            this.addEventListener('loadstart', () => {
              (window as any).__superwizard_pending_xhr_count++;
            });
            
            this.addEventListener('loadend', () => {
              (window as any).__superwizard_pending_xhr_count = Math.max(0, (window as any).__superwizard_pending_xhr_count - 1);
            });
            
            return originalOpen.call(this, method, url, async, username, password);
          };

          // Simple timer monitoring
          let timerCount = 0;
          const incrementTimer = () => {
            timerCount = Math.min(timerCount + 1, 10);
            (window as any).__superwizard_pending_timer_count = timerCount;
            
            setTimeout(() => {
              timerCount = Math.max(0, timerCount - 1);
              (window as any).__superwizard_pending_timer_count = timerCount;
            }, 500);
          };

          // Track rapid DOM changes as proxy for timer activity
          let lastMutationTime = Date.now();
          const checkMutationFrequency = () => {
            const now = Date.now();
            if (now - lastMutationTime < 100) {
              incrementTimer();
            }
            lastMutationTime = now;
          };

          if ((window as any).__superwizard_mutation_observer) {
            (window as any).__superwizard_timer_check = checkMutationFrequency;
          }
          
          (window as any).__superwizard_network_monitor = true;
        }
      }
    });
  } catch (error) {
    console.warn('Failed to set up comprehensive monitoring:', error);
  }
  
  try {
    await checkPageLoadingAndStability(tabId);
    lastStabilityCheck = now;
    lastStabilityResult = true;
  } catch (error) {
    lastStabilityResult = false;
    throw error;
  }
} 