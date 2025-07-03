/**
 * errorBuilder.ts
 * 
 * Utility functions for building detailed error messages
 */

/**
 * Build operation context information for error messages
 */
export function buildOperationContext(operation: string, elementId: number, context: any): string {
  let message = `${operation} operation failed for element ${elementId}. `;
  
  // Add element type information if available
  if (context.elementType && context.elementType !== 'unknown') {
    message += `Element type: ${context.elementType}. `;
  }
  
  return message;
}

/**
 * Build scroll status information for error messages
 */
export function buildScrollStatus(context: any): string {
  if (!context.scrollAttempted) {
    return 'Scroll: Not attempted. ';
  }
  
  if (context.scrollSuccess) {
    return 'Scroll: ✓ Successful. ';
  } else if (context.scrollPartialSuccess) {
    return 'Scroll: ⚠ Partially successful. ';
  } else {
    return 'Scroll: ✗ Failed. ';
  }
}

/**
 * Build coordinate status information for error messages
 */
export function buildCoordinateStatus(context: any): string {
  if (context.coordinatesObtained) {
    const coords = context.coordinates;
    return `Coordinates: ✓ Obtained${coords ? ` (${coords.x}, ${coords.y})` : ''}. `;
  } else {
    return 'Coordinates: ✗ Failed to obtain. ';
  }
}

/**
 * Build cursor status information for error messages
 */
export function buildCursorStatus(context: any): string {
  if (context.cursorMoved) {
    return 'Cursor: ✓ Moved. ';
  } else {
    return 'Cursor: ✗ Not moved. ';
  }
}

/**
 * Add the last error to error messages
 */
export function addLastError(context: any): string {
  if (context.lastError) {
    return `Last error: ${context.lastError}`;
  }
  return '';
} 