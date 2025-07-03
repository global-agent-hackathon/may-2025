/**
 * DOM-related helper functions for manipulation and analysis
 */

import * as domActionsNoDebugger from './ScriptingMode';
import { useAppState } from '../../state/store';

// Define the common ActionName type
type ActionName = 'click' | 'setValue' | 'navigate';

// Define the payload types for each action
type ActionPayload<T extends ActionName> = T extends 'click' 
  ? { elementId: number }
  : T extends 'setValue'
  ? { elementId: number; value: string }
  : T extends 'navigate'
  ? { url: string }
  : never;

// Export the callDOMAction function that always uses the scripting mode
export const callDOMAction = async <T extends ActionName>(
  type: T,
  payload: ActionPayload<T>
): Promise<void> => {
  const actions = domActionsNoDebugger;
  
  // Type assertion to ensure TypeScript understands the compatibility
  const action = actions.callDOMAction as (type: T, payload: ActionPayload<T>) => Promise<void>;
  
  try {
    return await action(type, payload);
  } catch (error: any) {
    console.error(`Error in ${type} action:`, error);
    throw new Error(`Action failed: ${error.message || 'Unknown error'}`);
  }
};

export * from './simplifyDom';
export * from '../ai/availableActions'; 