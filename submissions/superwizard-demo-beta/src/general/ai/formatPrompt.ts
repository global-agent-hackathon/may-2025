import { ParsedResponseSuccess } from './parseResponse';
import { getCurrentTab } from '../utils/utils';

export async function formatPrompt(
    taskInstructions: string,
    previousActions: ParsedResponseSuccess[],
    pageContents: string,
    fullHistory: any[] = []
  ) {
    // Group messages and their corresponding actions
    type MessageGroup = {
      message: string;
      actions: ParsedResponseSuccess[];
    };
    
    const messageGroups: MessageGroup[] = [];
    
    // Extract all user messages and organize them with corresponding actions
    if (fullHistory && fullHistory.length > 0) {
      // First, collect all user messages
      const userEntries = fullHistory.filter(entry => entry.prompt && !entry.response);
      
      // For each user message, find subsequent AI actions until the next user message
      userEntries.forEach((userEntry, index) => {
        const nextUserEntryIndex = index + 1 < userEntries.length ? 
          fullHistory.indexOf(userEntries[index + 1]) : 
          fullHistory.length;
        
        const currentEntryIndex = fullHistory.indexOf(userEntry);
        
        // Get all AI responses between this message and the next user message
        const relatedActions: ParsedResponseSuccess[] = [];
        for (let i = currentEntryIndex + 1; i < nextUserEntryIndex; i++) {
          const entry = fullHistory[i];
          if (entry.action && !('error' in entry.action) && 'parsedAction' in entry.action) {
            // Convert entry to ParsedResponseSuccess format if possible
            const action = entry.action as ParsedResponseSuccess;
            relatedActions.push(action);
          }
        }
        
        messageGroups.push({
          message: userEntry.prompt,
          actions: relatedActions
        });
      });
    }
    
    // Make sure the current instruction is included if it's not already
    if (!messageGroups.some(group => group.message === taskInstructions)) {
      messageGroups.push({
        message: taskInstructions,
        actions: []
      });
    }
    
    // Format the message groups
    let promptContent = 'The user requests the following task:\n\n';
    
    // Format all user messages with their corresponding actions
    messageGroups.forEach((group, idx) => {
      promptContent += `User message ${idx + 1} -\n${group.message}\n\n`;
      
      if (group.actions.length > 0) {
        const serializedActions = group.actions
          .map(
            (action) =>
              `<Steps>${action.steps}</Steps>\n` +
              `<Thought>${action.thought}</Thought>\n` +
              `<Validator>${action.validator}</Validator>`
          )
          .join('\n\n');
        promptContent += `Actions taken for this task so far: \n${serializedActions}\n\n`;
      }
    });
    
    // Get current tab URL
    const activeTab = await getCurrentTab();
    const currentUrl = activeTab?.url || 'No URL available';
    
    // Add current time, URL and page contents
    promptContent += `Current time: ${new Date().toLocaleString()}\n\n`;
    promptContent += `Current page URL: ${currentUrl}\n\n`;
    promptContent += `Current page contents:\n${pageContents}`;
    
    return promptContent;
  }