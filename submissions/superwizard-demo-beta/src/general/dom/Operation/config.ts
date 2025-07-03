/**
 * config.ts
 * 
 * Configuration settings for DOM operations
 */

export const CONFIG = {
  SCROLL: {
    MAX_RETRIES: 3,
    RETRY_DELAY_BASE: 50,        // Reduced from 75ms to 50ms
    VISIBLE_WAIT_TIME: 150,      // Reduced from 200ms to 150ms
    CHECK_INTERVAL: 30,          // Reduced from 50ms to 30ms
    MIN_SMOOTH_TIMEOUT: 100,     // Reduced from 150ms to 100ms
    MAX_SMOOTH_TIMEOUT: 300,     // Reduced from 500ms to 300ms
    VIEWPORT_TOLERANCE: 10,
  },
  COORDINATES: {
    MAX_RETRIES: 3,
    RETRY_DELAY: 75,             // Reduced from 150ms to 75ms
    VIEWPORT_MARGIN: 50,
    MAX_COORDINATE_VALUE: 10000,
  },
  CLICK: {
    WAIT_AFTER_SCROLL: 25,       // Reduced from 50ms to 25ms
    WAIT_AFTER_CLICK: 50,        // Reduced from 75ms to 50ms
  },
  NAVIGATION: {
    TIMEOUT: 20000,
    WAIT_AFTER_COMPLETE: 300,    // Reduced from 500ms to 300ms
  },
  PAGE_STABILITY: {
    TIMEOUT: 2000,               // Increased from 500ms to 2000ms for comprehensive checks
    POLL_INTERVAL: 25,           // Increased from 10ms to 25ms to reduce overhead
    CONSISTENT_CHECKS_REQUIRED: 2, // Increased back to 2 for more reliable stability
    MIN_STABLE_TIME: 100,        // Increased from 10ms to 100ms for better stability
    MAX_MUTATION_COUNT: 3,       // Keep at 3 - more lenient
    SKIP_STABILITY_THRESHOLD: 500, // Increased from 200ms to 500ms
  }
}; 