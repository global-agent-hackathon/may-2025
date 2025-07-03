import { ActionPayload, availableActions } from './availableActions';

export type ParsedResponseSuccess = {
  thought: string;
  action: string;
  parsedAction: ActionPayload;
  steps: string;
  validator: string;
};

export type ParsedResponse =
  | ParsedResponseSuccess
  | { error: string };

// Parse comma-separated arguments, respecting quotes
function parseArguments(argsString: string): string[] {
  const args: string[] = [];
  
  // Handle empty args case
  if (!argsString.trim()) return [];
  
  let inQuote = false;
  let quoteChar = '';
  let currentArg = '';
  
  for (let i = 0; i < argsString.length; i++) {
    const char = argsString[i];
    
    // Handle quote characters
    if ((char === '"' || char === "'" || char === '`') && (!inQuote || char === quoteChar)) {
      inQuote = !inQuote;
      quoteChar = inQuote ? char : '';
      currentArg += char;
    }
    // Handle commas (only split if not in quotes)
    else if (char === ',' && !inQuote) {
      if (currentArg.trim()) {
        args.push(currentArg.trim());
      }
      currentArg = '';
    }
    // Handle all other characters
    else {
      currentArg += char;
    }
  }
  
  // Add the last argument if it exists
  if (currentArg.trim()) {
    args.push(currentArg.trim());
  }
  
  return args;
}

export function parseResponse(text: string): ParsedResponse {
  // Extract sections using regex
  const sections = {
    thought: text.match(/<Thought>([\s\S]*?)<\/Thought>/)?.[1]?.trim(),
    action: text.match(/<Action>([\s\S]*?)<\/Action>/)?.[1]?.trim(),
    steps: text.match(/<Steps>([\s\S]*?)<\/Steps>/)?.[1]?.trim() || '',
    validator: text.match(/<Validator>([\s\S]*?)<\/Validator>/)?.[1]?.trim()
  };
  
  // Check for required sections only (excluding steps which is optional)
  const requiredSections = ['thought', 'action', 'validator'] as const;
  for (const key of requiredSections) {
    if (!sections[key]) {
      return { error: `Invalid response: ${key} not found in the model response.` };
    }
  }
  
  // Parse action string (format: functionName(arg1, arg2, ...))
  const actionPattern = /(\w+)\(([^]*)\)/;
  const actionParts = sections.action!.match(actionPattern);
  
  if (!actionParts) {
    return {
      error: 'Invalid action format: Action should be in the format functionName(arg1, arg2, ...).'
    };
  }
  
  const [, actionName, actionArgsString] = actionParts;
  
  // Find the action in available actions
  const availableAction = availableActions.find(action => action.name === actionName);
  
  if (!availableAction) {
    return { error: `Invalid action: "${actionName}" is not a valid action.` };
  }
  
  // Parse and validate arguments
  const argsArray = parseArguments(actionArgsString);
  
  // Special handling for "respond" action - allow 1 or more arguments
  if (actionName === 'respond') {
    if (argsArray.length < 1) {
      return {
        error: `Invalid number of arguments: Expected at least 1 for action "${actionName}", but got ${argsArray.length}.`
      };
    }
  } else {
    // For all other actions, maintain strict validation
    if (argsArray.length !== availableAction.args.length) {
      return {
        error: `Invalid number of arguments: Expected ${availableAction.args.length} for action "${actionName}", but got ${argsArray.length}.`
      };
    }
  }
  
  // Process arguments according to their expected types
  const parsedArgs: Record<string, number | string | string[]> = {};
  
  if (actionName === 'respond') {
    // For respond action, treat all arguments as strings and combine them
    const messages: string[] = [];
    for (let i = 0; i < argsArray.length; i++) {
      const arg = argsArray[i];
      // Extract string without quotes if present
      const isQuoted = /^["'`][\s\S]*["'`]$/.test(arg);
      if (!isQuoted) {
        return { error: `Invalid argument type: Expected a string for argument ${i + 1}, but got "${arg}".` };
      }
      messages.push(arg.slice(1, -1));
    }
    // Store the first message as 'message' for compatibility and all messages as 'messages'
    parsedArgs['message'] = messages[0];
    if (messages.length > 1) {
      parsedArgs['messages'] = messages;
    }
  } else {
    // For all other actions, process normally
    for (let i = 0; i < argsArray.length; i++) {
      const arg = argsArray[i];
      const { name, type } = availableAction.args[i];
      
      if (type === 'number') {
        const numberValue = Number(arg);
        if (isNaN(numberValue)) {
          return { error: `Invalid argument type: Expected a number for argument "${name}", but got "${arg}".` };
        }
        parsedArgs[name] = numberValue;
      } 
      else if (type === 'string') {
        // Extract string without quotes if present
        const isQuoted = /^["'`][\s\S]*["'`]$/.test(arg);
        if (!isQuoted) {
          return { error: `Invalid argument type: Expected a string for argument "${name}", but got "${arg}".` };
        }
        parsedArgs[name] = arg.slice(1, -1);
      } 
      else {
        return { error: `Invalid argument type: Unknown type "${type}" for argument "${name}".` };
      }
    }
  }
  
  // Create the final response object
  return {
    thought: sections.thought!,
    action: sections.action!,
    parsedAction: {
      name: availableAction.name,
      args: parsedArgs
    } as ActionPayload,
    steps: sections.steps!,
    validator: sections.validator!
  };
}
