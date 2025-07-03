import { TaskProgress } from '../../state/currentTask';

export interface ActionResult {
  success: boolean;
  status: 'success' | 'pending' | 'failure';
  message: string;
}

export function validateTaskAction(
  action: string,
  result: any,
  validationRules: NonNullable<TaskProgress['validationRules']>,
  currentProgress?: { completed: number; total: number }
): ActionResult {
  const resultStr = result?.toString() || '';

  // If we've already completed the required number of actions, prevent further actions
  if (currentProgress && currentProgress.completed >= currentProgress.total) {
    return {
      success: false,
      status: 'failure',
      message: 'Task already completed - no more actions allowed'
    };
  }

  // Check for success indicators
  if (validationRules.successIndicators.some(indicator => 
    resultStr.toLowerCase().includes(indicator.toLowerCase()))) {
    const isComplete = currentProgress && (currentProgress.completed + 1) >= currentProgress.total;
    return {
      success: true,
      status: isComplete ? 'success' : 'success',
      message: isComplete ? 'Task completed successfully' : 'Action completed successfully'
    };
  }

  // Check for pending state
  if (validationRules.pendingIndicators.some(indicator => 
    resultStr.toLowerCase().includes(indicator.toLowerCase()))) {
    return {
      success: true,
      status: 'pending',
      message: 'Action is in pending state'
    };
  }

  // Check for failure indicators
  if (validationRules.failureIndicators.some(indicator => 
    resultStr.toLowerCase().includes(indicator.toLowerCase()))) {
    return {
      success: false,
      status: 'failure',
      message: 'Action failed'
    };
  }

  // Default case - if no indicators match
  return {
    success: false,
    status: 'failure',
    message: 'Unable to validate action result'
  };
}

export function parseTaskRequirements(instructions: string): {
  total: number;
  type: string;
  validationRules: NonNullable<TaskProgress['validationRules']>
} {
  // Default validation rules
  const defaultRules = {
    successIndicators: ['success', 'completed', 'done'],
    pendingIndicators: ['pending', 'processing', 'waiting'],
    failureIndicators: ['failed', 'error', 'unable']
  };

  // Parse task type and quantity
  const numericMatch = instructions.match(/(\d+)\s+(\w+)/i);
  const type = numericMatch ? numericMatch[2].toLowerCase() : 'generic';
  const total = numericMatch ? parseInt(numericMatch[1]) : 0;

  // Task-specific validation rules
  const validationRules: Record<string, typeof defaultRules> = {
    connections: {
      successIndicators: ['request sent', 'connected', 'invitation sent'],
      pendingIndicators: ['pending', 'awaiting response'],
      failureIndicators: ['failed', 'error', 'unable to connect']
    },
    messages: {
      successIndicators: ['message sent', 'delivered'],
      pendingIndicators: ['sending', 'processing'],
      failureIndicators: ['failed to send', 'error']
    },
    likes: {
      successIndicators: ['liked', 'reaction added'],
      pendingIndicators: ['processing'],
      failureIndicators: ['failed to like', 'error']
    },
    comments: {
      successIndicators: ['comment posted', 'reply added'],
      pendingIndicators: ['posting', 'processing'],
      failureIndicators: ['failed to post', 'error']
    }
  };

  return {
    total,
    type,
    validationRules: validationRules[type] || defaultRules
  };
} 