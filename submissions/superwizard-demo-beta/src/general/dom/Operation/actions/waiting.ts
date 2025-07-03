/**
 * waiting.ts
 * 
 * Waiting functionality for DOM operations
 * Allows the AI to pause execution for a specified duration
 */

import { CONFIG } from '../config';
import { WaitingResult } from '../types';

/**
 * Wait for a specified number of seconds
 * @param payload Object containing the number of seconds to wait
 * @returns Promise that resolves after the specified time
 */
export async function waiting(payload: { seconds: number }): Promise<void> {
  const { seconds } = payload;
  
  // Validate input
  if (typeof seconds !== 'number' || seconds < 0) {
    throw new Error(`Invalid wait duration: ${seconds}. Must be a non-negative number.`);
  }
  
  // Set reasonable limits to prevent infinite waits
  const maxWaitSeconds = 300; // 5 minutes maximum
  const actualWaitSeconds = Math.min(seconds, maxWaitSeconds);
  
  if (seconds > maxWaitSeconds) {
    console.warn(`Wait duration capped at ${maxWaitSeconds} seconds (requested: ${seconds} seconds)`);
  }
  
  // Convert to milliseconds
  const waitMs = actualWaitSeconds * 1000;
  
  console.log(`Waiting for ${actualWaitSeconds} seconds...`);
  
  const startTime = Date.now();
  
  return new Promise((resolve) => {
    setTimeout(() => {
      const actualDuration = (Date.now() - startTime) / 1000;
      console.log(`Wait completed. Requested: ${actualWaitSeconds}s, Actual: ${actualDuration.toFixed(2)}s`);
      resolve();
    }, waitMs);
  });
} 