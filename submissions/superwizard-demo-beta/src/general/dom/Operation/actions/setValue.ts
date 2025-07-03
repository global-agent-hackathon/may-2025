/**
 * setValue.ts
 * 
 * Enhanced setValue functionality with proper completion signaling
 * Handles typing character by character with realistic delays and proper event dispatch
 */

import { CONFIG } from '../config';
import { sleep } from '../../../utils/utils';
import { getElementByNodeId, executeScript } from '../core/element';
import { getCenterCoordinates } from '../core/coordinates';
import { scrollIntoView } from './scroll';
import { click } from './click';
import { initializeCursor, moveCursor, hideCursor } from '../core/cursor';
import { NODE_ID_SELECTOR } from '../../../../constants';
import { ElementCoordinates, SetValueResult } from '../types';

interface OperationContext {
  scrollAttempted: boolean;
  scrollSuccess: boolean;
  scrollPartialSuccess: boolean;
  clickAttempted: boolean;
  clickSuccess: boolean;
  coordinatesObtained: boolean;
  cursorMoved: boolean;
  primarySetValueAttempted: boolean;
  fallbackSetValueAttempted: boolean;
  elementType: string;
  lastError: string | null;
}

/**
 * Enhanced setValue that properly signals completion after typing animation
 */
export async function setValue(payload: { elementId: number; value: string }): Promise<void> {
  const { elementId, value: rawValue } = payload;
  
  // Process the value (handle line breaks, etc.)
  const processedValue = rawValue.replace(/\\n/g, '\n');
  
  const operationContext: OperationContext = {
    scrollAttempted: false,
    scrollSuccess: false,
    scrollPartialSuccess: false,
    clickAttempted: false,
    clickSuccess: false,
    coordinatesObtained: false,
    cursorMoved: false,
    primarySetValueAttempted: false,
    fallbackSetValueAttempted: false,
    elementType: 'unknown',
    lastError: null
  };

  try {
    await initializeCursor();
    
    // Prepare element (scroll, click, focus)
    await prepareElement(elementId, operationContext);
    
    // Attempt cursor movement
    await attemptCursorMovement(elementId, operationContext);
    
    // Try primary setValue method with completion tracking
    operationContext.primarySetValueAttempted = true;
    
    return new Promise<void>((resolve, reject) => {
      // Execute the typing with completion callback
      executeSetValueWithCompletion(elementId, processedValue, operationContext)
        .then(() => {
          console.log(`setValue completed for element ${elementId}`);
          resolve();
        })
        .catch(async (primaryError) => {
          console.warn('Primary setValue failed, trying fallback:', primaryError);
          
          // Try fallback method
          operationContext.fallbackSetValueAttempted = true;
          
          try {
            await executeSetValueFallback(elementId, processedValue, operationContext);
            console.log(`setValue fallback completed for element ${elementId}`);
            resolve();
          } catch (fallbackError) {
            const errorMessage = buildSetValueErrorMessage(elementId, operationContext);
            console.error(errorMessage);
            reject(new Error(errorMessage));
          }
        });
    });

  } catch (error) {
    await hideCursor();
    console.error('Error in setValue:', error);
    throw new Error(`Failed to set value: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Execute setValue with proper completion tracking
 */
async function executeSetValueWithCompletion(
  elementId: number, 
  value: string, 
  context: OperationContext
): Promise<void> {
  const { uniqueId } = await getElementByNodeId(elementId);
  
  return new Promise<void>((resolve, reject) => {
    // Calculate total duration for typing animation
    const typingDuration = value.length * 50; // 50ms per character
    const totalDuration = typingDuration + 100; // Add 100ms buffer for final events
    
    // Execute the typing script
    executeScript(enhancedSetValueScript, uniqueId, NODE_ID_SELECTOR, value)
      .then((result: any) => {
        if (!result?.success) {
          reject(new Error(`Primary setValue failed: ${result?.reason || 'Unknown error'}`));
          return;
        }
        
        context.elementType = result.type || 'unknown';
        
        // Set a timer for when typing should be complete
        setTimeout(async () => {
          try {
            await hideCursor();
            console.log(`Typing animation completed for ${value.length} characters`);
            resolve();
          } catch (error) {
            await hideCursor();
            reject(error);
          }
        }, totalDuration);
        
      })
      .catch((error: any) => {
        reject(error);
      });
  });
}

/**
 * Execute fallback setValue method
 */
async function executeSetValueFallback(
  elementId: number, 
  value: string, 
  context: OperationContext
): Promise<void> {
  const { uniqueId } = await getElementByNodeId(elementId);
  
  const fallbackResult = await executeScript(fallbackSetValueScript, uniqueId, NODE_ID_SELECTOR, value);
  
  if (!fallbackResult?.success) {
    throw new Error(`Fallback setValue failed: ${fallbackResult?.reason || 'Unknown error'}`);
  }
  
  context.elementType = fallbackResult.type || 'unknown';
  
  // Even fallback should wait a short time for any events to process
  await sleep(200);
  await hideCursor();
}

/**
 * Enhanced setValue script that provides better completion timing
 */
const enhancedSetValueScript = (uniqueId: string, selector: string, value: string) => {
  const element = document.querySelector(`[${selector}="${uniqueId}"]`) as HTMLElement;
  if (!element) return { success: false, reason: 'Element not found', type: 'unknown' };
  
  const elementType = element.tagName.toLowerCase();
  const inputType = element instanceof HTMLInputElement ? element.type : 'N/A';
  
  try {
    element.focus();
  } catch (e) {
    return { success: false, reason: 'Element not focusable', type: elementType, inputType };
  }

  // Handle Draft.js editor with proper timing
  const draftEditor = element.closest('.DraftEditor-root');
  if (draftEditor) {
    const editorContent = draftEditor.querySelector('.public-DraftEditor-content') as HTMLElement;
    if (!editorContent) {
      return { success: false, reason: 'Could not find Draft.js editor content', type: 'draft-editor' };
    }

    editorContent.focus();
    
    // Clear content with Ctrl/Cmd+A
    const clearEvent = new KeyboardEvent('keydown', {
      key: 'a', code: 'KeyA', ctrlKey: true, metaKey: true, bubbles: true, cancelable: true
    });
    editorContent.dispatchEvent(clearEvent);

    // Type each character for Draft.js with proper delays
    value.split('').forEach((char, index) => {
      setTimeout(() => {
        if (char === '\n') {
          // Draft.js Enter handling
          const enterEvents = ['keydown', 'keypress', 'keyup'].map(type => 
            new KeyboardEvent(type, {
              key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
              bubbles: true, cancelable: true, composed: true
            })
          );
          
          enterEvents.forEach(event => editorContent.dispatchEvent(event));
          
          // Insert line break
          if (!document.execCommand?.('insertLineBreak', false)) {
            document.execCommand?.('insertHTML', false, '<br>');
          }
        } else {
          // Regular character for Draft.js
          const keyCode = char.charCodeAt(0);
          const eventInit = {
            key: char, code: `Key${char.toUpperCase()}`, keyCode, which: keyCode,
            shiftKey: char === char.toUpperCase() && char !== char.toLowerCase(),
            bubbles: true, cancelable: true, composed: true
          };

          // Dispatch events
          ['beforeinput', 'keydown', 'keypress', 'input', 'keyup'].forEach(type => {
            let event;
            if (type === 'beforeinput' || type === 'input') {
              event = new InputEvent(type, { 
                bubbles: true, cancelable: true, data: char, inputType: 'insertText' 
              });
            } else {
              event = new KeyboardEvent(type, eventInit);
            }
            editorContent.dispatchEvent(event);
          });

          document.execCommand('insertText', false, char);
        }
        
        // Final change event after last character
        if (index === value.length - 1) {
          setTimeout(() => {
            editorContent.dispatchEvent(new Event('change', { bubbles: true }));
          }, 50);
        }
      }, index * 50);
    });

    return { success: true, type: 'draft-editor' };
  }

  // Clear existing content
  if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
    element.value = '';
  } else if (element.isContentEditable) {
    element.textContent = '';
  }

  // Type each character with proper events and timing
  value.split('').forEach((char, index) => {
    setTimeout(() => {
      if (char === '\n') {
        // Handle Enter key based on element type
        const isTextarea = element instanceof HTMLTextAreaElement;
        const isContentEditable = element.isContentEditable;
        const isInput = element instanceof HTMLInputElement;
        
        // Create and dispatch Enter events
        const enterEvents = ['keydown', 'keypress', 'keyup'].map(type => 
          new KeyboardEvent(type, {
            key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
            bubbles: true, cancelable: true
          })
        );
        
        const prevented = !element.dispatchEvent(enterEvents[0]);
        if (!prevented) element.dispatchEvent(enterEvents[1]);
        element.dispatchEvent(enterEvents[2]);
        
        // Insert newline based on element type
        if (isTextarea) {
          const textarea = element as HTMLTextAreaElement;
          const pos = textarea.selectionStart || textarea.value.length;
          textarea.value = textarea.value.substring(0, pos) + '\n' + textarea.value.substring(pos);
          textarea.selectionStart = textarea.selectionEnd = pos + 1;
        } else if (isContentEditable) {
          document.execCommand?.('insertLineBreak', false) || 
          document.execCommand?.('insertHTML', false, '<br>');
        } else if (isInput && !prevented) {
          // Try form submission
          const form = element.closest('form');
          if (form) {
            try {
              const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
              if (form.dispatchEvent(submitEvent)) form.submit();
            } catch (e) {
              (form.querySelector('button[type="submit"], input[type="submit"]') as HTMLElement)?.click();
            }
          }
        }
        
        element.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        // Type regular character
        const keyCode = char.charCodeAt(0);
        const eventInit = {
          key: char, code: `Key${char.toUpperCase()}`, keyCode, which: keyCode,
          shiftKey: char === char.toUpperCase() && char !== char.toLowerCase(),
          bubbles: true, cancelable: true
        };
        
        ['keydown', 'keypress', 'keyup'].forEach(type => {
          element.dispatchEvent(new KeyboardEvent(type, eventInit));
        });
        
        // Update content
        if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
          element.value += char;
        } else if (element.isContentEditable) {
          document.execCommand('insertText', false, char);
        }
        
        element.dispatchEvent(new Event('input', { bubbles: true }));
      }
      
      // Dispatch change after last character
      if (index === value.length - 1) {
        setTimeout(() => {
          element.dispatchEvent(new Event('change', { bubbles: true }));
        }, 50);
      }
    }, index * 50);
  });

  return { success: true, type: elementType, inputType };
};

/**
 * Prepare element for setValue (scroll, click, focus)
 */
async function prepareElement(elementId: number, context: OperationContext): Promise<void> {
  // Scroll element into view
  context.scrollAttempted = true;
  const scrollResult = await scrollIntoView(elementId);
  context.scrollSuccess = scrollResult.success;
  context.scrollPartialSuccess = scrollResult.partialSuccess;
  
  if (!scrollResult.success) {
    const message = scrollResult.partialSuccess ? 'Scroll partially succeeded' : 'Scroll failed';
    console.warn(`${message}: ${scrollResult.reason} - continuing with setValue`);
    context.lastError = `Scroll: ${scrollResult.reason}`;
  }
  
  // Try to click/focus element
  context.clickAttempted = true;
  try {
    await click({ elementId });
    context.clickSuccess = true;
  } catch (clickError) {
    console.warn('Click failed, trying direct focus:', clickError);
    context.lastError = `Click failed: ${clickError instanceof Error ? clickError.message : String(clickError)}`;
    
    // Try direct focus as fallback
    try {
      const { uniqueId } = await getElementByNodeId(elementId);
      const focusResult = await executeScript(directFocusScript, uniqueId, NODE_ID_SELECTOR);
      
      if (focusResult.success) {
        context.elementType = focusResult.type;
        console.log('Successfully focused element directly');
      }
    } catch (focusError) {
      console.warn('Direct focus also failed:', focusError);
      context.lastError = `Focus failed: ${focusError instanceof Error ? focusError.message : String(focusError)}`;
    }
  }

  await sleep(CONFIG.CLICK.WAIT_AFTER_CLICK);
}

/**
 * Attempt cursor movement if coordinates are available
 */
async function attemptCursorMovement(elementId: number, context: OperationContext): Promise<void> {
  try {
    const coordinates = await getCenterCoordinates(elementId);
    context.coordinatesObtained = true;
    context.cursorMoved = await moveCursor(coordinates.x, coordinates.y, 'simulateTyping');
    await sleep(CONFIG.CLICK.WAIT_AFTER_CLICK);
  } catch (coordError) {
    console.warn('Could not get coordinates for cursor movement:', coordError);
    context.lastError = `Coordinates failed: ${coordError instanceof Error ? coordError.message : String(coordError)}`;
  }
}

/**
 * Create keyboard event with common properties
 */
function createKeyboardEvent(type: string, char: string, options: Partial<KeyboardEventInit> = {}): KeyboardEvent {
  const keyCode = char.charCodeAt(0);
  const isUpperCase = char === char.toUpperCase() && char !== char.toLowerCase();
  
  return new KeyboardEvent(type, {
    key: char,
    code: `Key${char.toUpperCase()}`,
    keyCode,
    which: keyCode,
    charCode: type === 'keypress' ? keyCode : 0,
    shiftKey: isUpperCase,
    bubbles: true,
    cancelable: true,
    composed: true,
    ...options
  });
}

/**
 * Create Enter key event
 */
function createEnterEvent(type: string): KeyboardEvent {
  return new KeyboardEvent(type, {
    key: 'Enter',
    code: 'Enter',
    keyCode: 13,
    which: 13,
    charCode: type === 'keypress' ? 13 : 0,
    bubbles: true,
    cancelable: true,
    composed: true,
    detail: 0,
    view: window,
    location: 0,
    repeat: false,
    ctrlKey: false,
    shiftKey: false,
    altKey: false,
    metaKey: false
  });
}

/**
 * Dispatch input and change events
 */
function dispatchInputEvents(element: HTMLElement, inputType = 'insertText', data: string | null = null): void {
  // Dispatch input event
  try {
    const inputEvent = new InputEvent('input', {
      bubbles: true,
      cancelable: true,
      inputType,
      data,
      isComposing: false
    });
    element.dispatchEvent(inputEvent);
  } catch (e) {
    element.dispatchEvent(new Event('input', { bubbles: true }));
  }
  
  // Dispatch change event with delay
  setTimeout(() => {
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }, 50);
}

/**
 * Insert line break in contenteditable element
 */
function insertLineBreak(element: HTMLElement): boolean {
  const methods = [
    // Method 1: execCommand
    () => document.execCommand?.('insertLineBreak', false) || document.execCommand?.('insertHTML', false, '<br>'),
    
    // Method 2: Selection API with BR
    () => {
      const selection = window.getSelection();
      if (selection?.rangeCount) {
        const range = selection.getRangeAt(0);
        range.deleteContents();
        const br = document.createElement('br');
        range.insertNode(br);
        range.setStartAfter(br);
        range.setEndAfter(br);
        selection.removeAllRanges();
        selection.addRange(range);
        return true;
      }
      return false;
    },
    
    // Method 3: Direct content manipulation
    () => {
      element.innerHTML += '<br>';
      return true;
    }
  ];
  
  for (const method of methods) {
    try {
      if (method()) return true;
    } catch (e) {
      continue;
    }
  }
  
  return false;
}

/**
 * Handle Enter key for different element types
 */
function handleEnterKey(element: HTMLElement): void {
  const isTextarea = element instanceof HTMLTextAreaElement;
  const isContentEditable = element.isContentEditable && !element.closest('.DraftEditor-root');
  const isRegularInput = element instanceof HTMLInputElement;
  
  // Dispatch keyboard events
  const keydownEvent = createEnterEvent('keydown');
  const keypressEvent = createEnterEvent('keypress');
  const keyupEvent = createEnterEvent('keyup');
  
  const keydownPrevented = !element.dispatchEvent(keydownEvent);
  if (!keydownPrevented) {
    element.dispatchEvent(keypressEvent);
  }
  element.dispatchEvent(keyupEvent);
  
  // Handle element-specific behavior
  if (isTextarea) {
    const textarea = element as HTMLTextAreaElement;
    const currentValue = textarea.value;
    const selectionStart = textarea.selectionStart || currentValue.length;
    const selectionEnd = textarea.selectionEnd || currentValue.length;
    textarea.value = currentValue.substring(0, selectionStart) + '\n' + currentValue.substring(selectionEnd);
    textarea.selectionStart = textarea.selectionEnd = selectionStart + 1;
    dispatchInputEvents(element, 'insertLineBreak', null);
  } else if (isContentEditable) {
    insertLineBreak(element);
    dispatchInputEvents(element, 'insertLineBreak', null);
  } else if (isRegularInput && !keydownPrevented) {
    // Try form submission or search button click
    const form = element.closest('form');
    if (form) {
      try {
        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
        if (form.dispatchEvent(submitEvent)) {
          form.submit();
          return;
        }
      } catch (e) {
        // Try submit button click
        (form.querySelector('button[type="submit"], input[type="submit"]') as HTMLElement)?.click();
      }
    }
  }
}

/**
 * Type a single character with events
 */
function typeCharacter(element: HTMLElement, char: string): void {
  const events = ['keydown', 'keypress', 'keyup'] as const;
  
  events.forEach(eventType => {
    const event = createKeyboardEvent(eventType, char);
    element.dispatchEvent(event);
  });
  
  // Update element value/content
  if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
    element.value += char;
  } else if (element.isContentEditable) {
    document.execCommand('insertText', false, char);
  }
  
  dispatchInputEvents(element, 'insertText', char);
}

/**
 * Primary setValue script for page execution
 */
const primarySetValueScript = (uniqueId: string, selector: string, value: string) => {
  const element = document.querySelector(`[${selector}="${uniqueId}"]`) as HTMLElement;
  if (!element) return { success: false, reason: 'Element not found', type: 'unknown' };
  
  const elementType = element.tagName.toLowerCase();
  const inputType = element instanceof HTMLInputElement ? element.type : 'N/A';
  
  try {
    element.focus();
  } catch (e) {
    return { success: false, reason: 'Element not focusable', type: elementType, inputType };
  }

  // Handle Draft.js editor
  const draftEditor = element.closest('.DraftEditor-root');
  if (draftEditor) {
    const editorContent = draftEditor.querySelector('.public-DraftEditor-content') as HTMLElement;
    if (!editorContent) {
      return { success: false, reason: 'Could not find Draft.js editor content', type: 'draft-editor' };
    }

    editorContent.focus();
    
    // Clear content with Ctrl/Cmd+A
    const clearEvent = new KeyboardEvent('keydown', {
      key: 'a', code: 'KeyA', ctrlKey: true, metaKey: true, bubbles: true, cancelable: true
    });
    editorContent.dispatchEvent(clearEvent);

    // Type each character for Draft.js
    value.split('').forEach((char, index) => {
      setTimeout(() => {
        if (char === '\n') {
          // Draft.js Enter handling
          const enterEvents = ['keydown', 'keypress', 'keyup'].map(type => 
            new KeyboardEvent(type, {
              key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
              bubbles: true, cancelable: true, composed: true
            })
          );
          
          enterEvents.forEach(event => editorContent.dispatchEvent(event));
          
          // Insert line break
          if (!document.execCommand?.('insertLineBreak', false)) {
            document.execCommand?.('insertHTML', false, '<br>');
          }
        } else {
          // Regular character for Draft.js
          const keyCode = char.charCodeAt(0);
          const eventInit = {
            key: char, code: `Key${char.toUpperCase()}`, keyCode, which: keyCode,
            shiftKey: char === char.toUpperCase() && char !== char.toLowerCase(),
            bubbles: true, cancelable: true, composed: true
          };

          // Dispatch events
          ['beforeinput', 'keydown', 'keypress', 'input', 'keyup'].forEach(type => {
            let event;
            if (type === 'beforeinput' || type === 'input') {
              event = new InputEvent(type, { 
                bubbles: true, cancelable: true, data: char, inputType: 'insertText' 
              });
            } else {
              event = new KeyboardEvent(type, eventInit);
            }
            editorContent.dispatchEvent(event);
          });

          document.execCommand('insertText', false, char);
        }
        
        // Final change event
        if (index === value.length - 1) {
          setTimeout(() => {
            editorContent.dispatchEvent(new Event('change', { bubbles: true }));
          }, 50);
        }
      }, index * 50);
    });

    return { success: true, type: 'draft-editor' };
  }

  // Clear existing content
  if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
    element.value = '';
  } else if (element.isContentEditable) {
    element.textContent = '';
  }

  // Type each character with proper events
  value.split('').forEach((char, index) => {
    setTimeout(() => {
      if (char === '\n') {
        // Handle Enter key based on element type
        const isTextarea = element instanceof HTMLTextAreaElement;
        const isContentEditable = element.isContentEditable;
        const isInput = element instanceof HTMLInputElement;
        
        // Create and dispatch Enter events
        const enterEvents = ['keydown', 'keypress', 'keyup'].map(type => 
          new KeyboardEvent(type, {
            key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
            bubbles: true, cancelable: true
          })
        );
        
        const prevented = !element.dispatchEvent(enterEvents[0]);
        if (!prevented) element.dispatchEvent(enterEvents[1]);
        element.dispatchEvent(enterEvents[2]);
        
        // Insert newline based on element type
        if (isTextarea) {
          const textarea = element as HTMLTextAreaElement;
          const pos = textarea.selectionStart || textarea.value.length;
          textarea.value = textarea.value.substring(0, pos) + '\n' + textarea.value.substring(pos);
          textarea.selectionStart = textarea.selectionEnd = pos + 1;
        } else if (isContentEditable) {
          document.execCommand?.('insertLineBreak', false) || 
          document.execCommand?.('insertHTML', false, '<br>');
        } else if (isInput && !prevented) {
          // Try form submission
          const form = element.closest('form');
          if (form) {
            try {
              const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
              if (form.dispatchEvent(submitEvent)) form.submit();
            } catch (e) {
              (form.querySelector('button[type="submit"], input[type="submit"]') as HTMLElement)?.click();
            }
          }
        }
        
        element.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        // Type regular character
        const keyCode = char.charCodeAt(0);
        const eventInit = {
          key: char, code: `Key${char.toUpperCase()}`, keyCode, which: keyCode,
          shiftKey: char === char.toUpperCase() && char !== char.toLowerCase(),
          bubbles: true, cancelable: true
        };
        
        ['keydown', 'keypress', 'keyup'].forEach(type => {
          element.dispatchEvent(new KeyboardEvent(type, eventInit));
        });
        
        // Update content
        if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
          element.value += char;
        } else if (element.isContentEditable) {
          document.execCommand('insertText', false, char);
        }
        
        element.dispatchEvent(new Event('input', { bubbles: true }));
      }
      
      // Dispatch change after last character
      if (index === value.length - 1) {
        setTimeout(() => {
          element.dispatchEvent(new Event('change', { bubbles: true }));
        }, 50);
      }
    }, index * 50);
  });

  return { success: true, type: elementType, inputType };
};

/**
 * Fallback setValue script for direct value setting
 */
const fallbackSetValueScript = (uniqueId: string, selector: string, value: string) => {
  const element = document.querySelector(`[${selector}="${uniqueId}"]`) as HTMLElement;
  if (!element) return { success: false, reason: 'Element not found in fallback', type: 'unknown' };
  
  const elementType = element.tagName.toLowerCase();
  const inputType = element instanceof HTMLInputElement ? element.type : 'N/A';
  
  try {
    element.focus();
    
    if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
      element.value = value;
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
      return { success: true, method: 'direct-value', type: elementType, inputType };
    }
    
    if (element.isContentEditable) {
      element.textContent = value;
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
      return { success: true, method: 'direct-content', type: elementType };
    }
    
    return { success: false, reason: 'Element type not supported in fallback', type: elementType, inputType };
  } catch (error) {
    return { 
      success: false, 
      reason: error instanceof Error ? error.message : String(error),
      type: elementType, inputType
    };
  }
};

/**
 * Direct focus script
 */
const directFocusScript = (uniqueId: string, selector: string) => {
  const element = document.querySelector(`[${selector}="${uniqueId}"]`) as HTMLElement;
  if (element && typeof element.focus === 'function') {
    element.focus();
    return { success: true, type: element.tagName.toLowerCase() };
  }
  return { success: false, type: 'unknown' };
};

/**
 * Build detailed error message for setValue failures
 */
function buildSetValueErrorMessage(elementId: number, context: OperationContext): string {
  const status = (attempted: boolean, success: boolean, partial = false) => 
    !attempted ? 'Not attempted' : success ? '✓ Successful' : partial ? '⚠ Partially successful' : '✗ Failed';
  
  let message = `SetValue operation failed for element ${elementId}. `;
  
  if (context.elementType !== 'unknown') {
    message += `Element type: ${context.elementType}. `;
  }
  
  message += `Scroll: ${status(context.scrollAttempted, context.scrollSuccess, context.scrollPartialSuccess)}. `;
  message += `Click/Focus: ${status(context.clickAttempted, context.clickSuccess)}. `;
  message += `Coordinates: ${context.coordinatesObtained ? '✓ Obtained' : '✗ Failed to obtain'}. `;
  message += `Cursor: ${context.cursorMoved ? '✓ Moved' : '✗ Not moved'}. `;
  
  if (context.primarySetValueAttempted && context.fallbackSetValueAttempted) {
    message += 'Methods: Both primary and fallback failed. ';
  } else if (context.primarySetValueAttempted) {
    message += 'Methods: Primary failed, fallback not attempted. ';
  } else {
    message += 'Methods: Neither primary nor fallback attempted. ';
  }
  
  if (context.lastError) {
    message += `Last error: ${context.lastError}`;
  }
  
  return message;
} 