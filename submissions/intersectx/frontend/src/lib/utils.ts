import { clsx, type ClassValue } from 'clsx';

/**
 * Combines multiple class names or class value arrays into one string.
 * Used for conditional classes in components.
 * 
 * @param inputs - Any number of class values to be combined
 * @returns A string of combined class names
 */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

/**
 * Generates a globally unique ID
 * 
 * @returns A string representing a unique ID
 */
export function generateId(): string {
  return Math.random().toString(36).substring(2, 10);
}

/**
 * Formats a number to a UI-friendly currency format (e.g., 1000000 -> "1M")
 * 
 * @param value - The number or string value to format
 * @returns A formatted string representation of the value
 */
export function formatCurrency(value: string | number | undefined): string {
  if (!value) return '-';
  
  // Convert string to number if needed
  const num = typeof value === 'string' ? parseFloat(value.replace(/[^0-9.-]+/g, '')) : value;
  
  if (isNaN(num)) return '-';
  
  // Format based on magnitude
  if (num >= 1000000000) {
    return `$${(num / 1000000000).toFixed(1)}B`;
  } else if (num >= 1000000) {
    return `$${(num / 1000000).toFixed(1)}M`;
  } else if (num >= 1000) {
    return `$${(num / 1000).toFixed(0)}K`;
  } else {
    return `$${num.toFixed(0)}`;
  }
} 