import type { CompletionUsage } from 'openai/resources';
import { callDOMAction, waitForActionCompletion, hasActiveAction } from '../general/dom/ScriptingMode';
import { ensurePageStability } from '../general/dom/Operation/core/stability';
import {
  ParsedResponse,
  ParsedResponseSuccess,
  parseResponse,
} from '../general/ai/parseResponse';
import { determineNextAction } from '../general/ai/systemGateway';
import { getSimplifiedDom } from '../general/dom';
import { sleep, truthyFilter } from '../general/utils/utils';
import { validateTaskAction, parseTaskRequirements } from '../general/utils/validation';
import { MyStateCreator } from './store';
import { useAppState } from './store';

export type TaskHistoryEntry = {
  prompt: string;
  response: string;
  action: ParsedResponse;
  usage: CompletionUsage | null;
  timestamp: string;
  phase: 'user_input' | 'ai_response' | 'error';
  previousActions?: string[];
  pageContents?: string;
};

export interface TaskProgress {
  total: number;
  completed: number;
  type: string;
  validationRules?: {
    successIndicators: string[];
    failureIndicators: string[];
    pendingIndicators: string[];
  };
}

export interface CurrentTaskSlice {
  tabId: number;
  instructions: string | null;
  history: any[];
  status: 'idle' | 'running' | 'completed' | 'failed' | 'error' | 'success';
  actionStatus: 'idle' | 'initializing' | 'running-action' | 
    'pulling-dom' | 'transforming-dom' | 'performing-query' | 
    'performing-action' | 'waiting' | 'ai-recovery';
  taskProgress: TaskProgress;
  consecutiveFailures: number;
  lastActionResult: { success: boolean; error?: string; actionId?: string } | null;
  actions: {
    runTask: (onError?: (error: string) => void) => Promise<void>;
    updateTaskProgress: (progress: Partial<TaskProgress>) => void;
    validateAction: (actionType: string, result: any) => 'success' | 'pending' | 'failure';
    interrupt: () => void;
    clearHistory: () => void;
  };
}

export const createCurrentTaskSlice: MyStateCreator<CurrentTaskSlice> = (
  set,
  get
) => ({
  tabId: -1,
  instructions: null,
  history: [],
  status: 'idle',
  actionStatus: 'idle',
  taskProgress: {
    total: 0,
    completed: 0,
    type: '',
    validationRules: {
      successIndicators: [],
      failureIndicators: [],
      pendingIndicators: []
    }
  },
  consecutiveFailures: 0,
  lastActionResult: null,
  actions: {
    runTask: async (onError) => {
      const wasStopped = () => get().currentTask.status !== 'running';
      const setActionStatus = (status: CurrentTaskSlice['actionStatus']) => {
        set((state) => {
          state.currentTask.actionStatus = status;
        });
      };

      const ui = get().ui;
      const instructions = ui?.instructions;
      if (!instructions || get().currentTask.status === 'running') return;

      // First, add the user's message to the history
      set((state) => {
        // Get previous actions from history
        const previousActions = state.currentTask.history
          .filter(entry => entry.action && !('error' in entry.action))
          .map(entry => {
            if (entry.action && 'parsedAction' in entry.action) {
              const { name, args } = entry.action.parsedAction;
              return `${name}(${JSON.stringify(args)})`;
            }
            return '';
          })
          .filter(Boolean);

        // Add the user message to the history with additional context
        state.currentTask.history.push({
          prompt: instructions,
          response: '',
          action: null,
          usage: null,
          timestamp: new Date().toISOString(),
          previousActions,
          pageContents: '', // Will be populated with DOM contents later
          phase: 'user_input'
        });
        
        state.currentTask.instructions = instructions;
        state.currentTask.status = 'running';
        state.currentTask.actionStatus = 'initializing';
        
        // Parse task requirements from instructions
        const taskConfig = parseTaskRequirements(instructions);
        state.currentTask.taskProgress = {
          total: taskConfig.total,
          completed: 0,
          type: taskConfig.type,
          validationRules: taskConfig.validationRules
        };
      });

      try {
        const activeTab = (
          await chrome.tabs.query({ active: true, currentWindow: true })
        )[0];

        if (!activeTab.id) throw new Error('No active tab found');
        
        // Check if we're trying to interact with restricted URLs
        if (activeTab.url?.startsWith('chrome://') || 
            activeTab.url?.startsWith('chrome-extension://') || 
            activeTab.url?.startsWith('https://chrome.google.com/')) {
          // Automatically redirect to Google.com when we encounter Chrome system pages
          try {
            console.log('Redirecting from Chrome system page to Google.com');
            
            // Set the tabId first to ensure the navigation works correctly
            const tabId = activeTab.id;
            set((state) => {
              state.currentTask.tabId = tabId;
            });
            
            // Use the existing navigation function which handles tab updates properly
            await callDOMAction('navigate', { url: 'https://www.google.com' });
            
            // After navigation completes, continue with task execution on Google.com
            // Don't return from the function - simply continue execution
            // This ensures all the DOM extraction happens on Google.com
          } catch (navError) {
            console.error('Failed to redirect from Chrome system page:', navError);
            // If navigation fails, still throw the original error
            throw new Error('Cannot interact with Chrome system pages');
          }
        }
        
        const tabId = activeTab.id;
        set((state) => {
          state.currentTask.tabId = tabId;
        });

        // Ensure content script is loaded
        try {
          await chrome.tabs.sendMessage(tabId, { type: 'PING' });
        } catch (error) {
          // Content script not loaded, inject it
          await chrome.scripting.executeScript({
            target: { tabId },
            files: ['contentScript.bundle.js']
          });
          // Wait for content script to initialize
          await new Promise((resolve) => setTimeout(resolve, 300));
        }

        // eslint-disable-next-line no-constant-condition
        while (true) {
          if (wasStopped()) break;

          // Check for too many consecutive failures
          const currentFailures = get().currentTask.consecutiveFailures;
          const MAX_CONSECUTIVE_FAILURES = 3;
          
          if (currentFailures >= MAX_CONSECUTIVE_FAILURES) {
            console.error(`Task stopped due to ${MAX_CONSECUTIVE_FAILURES} consecutive action failures`);
            if (onError) {
              onError(`Task stopped: ${MAX_CONSECUTIVE_FAILURES} consecutive actions failed. The AI is unable to recover from these errors.`);
            }
            set((state) => {
              state.currentTask.status = 'error';
            });
            break;
          }

          // Wait for any previous action to complete before proceeding
          if (hasActiveAction()) {
            console.log('Waiting for previous action to complete...');
            await waitForActionCompletion();
            console.log('Previous action completed, proceeding...');
          }

          setActionStatus('pulling-dom');
          
          // Update status to show recovery if we have failures
          if (get().currentTask.consecutiveFailures > 0) {
            setActionStatus('ai-recovery');
          }
          
          // Ensure page is stable before gathering DOM data
          await ensurePageStability(tabId);
          
          const pageDOM = await getSimplifiedDom();
          // No need to check for null since getSimplifiedDom now always returns a string or object

          // If stopped, break the loop
          if (wasStopped()) break;
          setActionStatus('transforming-dom');
          // Store DOM content for use in history and AI tasks
          const currentDom = typeof pageDOM === 'string' ? pageDOM : (pageDOM as { content: string }).content;

          // Update the latest history entry with page contents
          set((state) => {
            const lastEntry = state.currentTask.history[state.currentTask.history.length - 1];
            if (lastEntry && lastEntry.phase === 'user_input') {
              lastEntry.pageContents = currentDom;
            }
          });

          const previousActions = get()
            .currentTask.history.map((entry) => entry.action)
            .filter(truthyFilter);

          setActionStatus('performing-query');

          const actionResponse = await determineNextAction(
            instructions,
            previousActions.filter(
              (pa) => !('error' in pa)
            ) as any[],
            currentDom,
            3,
            onError
          );

          if (!actionResponse) {
            set((state) => {
              state.currentTask.status = 'error';
            });
            break;
          }

          if (wasStopped()) break;

          setActionStatus('performing-action');
          
          // Create the response text for parsing
          const responseText = `<Thought>${actionResponse.thought}</Thought>
<Action>${actionResponse.action}</Action>
<Steps>${actionResponse.steps}</Steps>
<Validator>${actionResponse.validator}</Validator>`;
          
          const action = parseResponse(responseText);
          
          set((state) => {
            state.currentTask.history.push({
              prompt: actionResponse.fullPrompt || instructions, // Use the full formatted prompt if available
              response: responseText, // Use the constructed response
              action,
              usage: actionResponse.usage,
              timestamp: new Date().toISOString(),
              phase: 'ai_response'
            });
          });

          if ('error' in action) {
            if (onError) {
              onError(action.error);
            }
            break;
          }

          // Handle task completion based on action type
          if (action.parsedAction.name === 'finish' || action.parsedAction.name === 'fail' || action.parsedAction.name === 'respond') {
            set((state) => {
              state.currentTask.status = action.parsedAction.name === 'finish' ? 'success' : 
                                       action.parsedAction.name === 'fail' ? 'error' : 
                                       'idle';
            });
            break;
          }

          // Execute the action and wait for completion
          try {
            let actionResult;
            if (action.parsedAction.name === 'click') {
              actionResult = await callDOMAction('click', action.parsedAction.args);
            } else if (action.parsedAction.name === 'setValue') {
              actionResult = await callDOMAction('setValue', action.parsedAction.args);
            } else if (action.parsedAction.name === 'navigate') {
              actionResult = await callDOMAction('navigate', action.parsedAction.args);
            } else if (action.parsedAction.name === 'waiting') {
              actionResult = await callDOMAction('waiting', action.parsedAction.args);
            } else if (action.parsedAction.name === 'memory') {
              // Memory action just stores the information and continues
              console.log('Memory stored:', action.parsedAction.args.message);
            }

            // Enhanced action result handling with immediate error notification
            if (actionResult) {
              console.log(`Action ${action.parsedAction.name} completed:`, actionResult.success ? 'Success' : 'Failed');
              
              // Update last action result in state
              set((state) => {
                state.currentTask.lastActionResult = {
                  success: actionResult.success,
                  error: actionResult.error,
                  actionId: actionResult.actionId
                };
              });
              
              if (!actionResult.success) {
                console.warn(`Action error: ${actionResult.error}`);
                
                // Increment consecutive failure counter
                set((state) => {
                  state.currentTask.consecutiveFailures += 1;
                });
                
                // Immediately notify user of action failure
                if (onError) {
                  const failureCount = get().currentTask.consecutiveFailures;
                  const userFriendlyError = `Action "${action.parsedAction.name}" failed (${failureCount}/3): ${
                    actionResult.error ? 
                    (actionResult.error.length > 100 ? actionResult.error.substring(0, 100) + '...' : actionResult.error) :
                    'Unknown error occurred'
                  }`;
                  onError(userFriendlyError);
                }
                
                // Add error entry to history for AI context
                set((state) => {
                  state.currentTask.history.push({
                    prompt: '',
                    response: '',
                    action: { error: actionResult.error || 'Action failed' },
                    usage: null,
                    timestamp: new Date().toISOString(),
                    phase: 'error'
                  });
                });
                
                // Continue with AI recovery (don't break the loop)
                console.log(`Action failed, continuing with AI recovery. Error: ${actionResult.error}`);
              } else {
                // Reset consecutive failures on success
                set((state) => {
                  state.currentTask.consecutiveFailures = 0;
                });
              }
            }

            // Wait for the action to be fully complete (including any animations)
            await waitForActionCompletion();
            console.log(`Action ${action.parsedAction.name} fully completed, ready for next iteration`);

          } catch (actionError) {
            console.error(`Error executing action ${action.parsedAction.name}:`, actionError);
            
            // Increment consecutive failure counter for exceptions
            set((state) => {
              state.currentTask.consecutiveFailures += 1;
              state.currentTask.lastActionResult = {
                success: false,
                error: actionError instanceof Error ? actionError.message : String(actionError)
              };
            });
            
            // Immediately notify user of action exception
            if (onError) {
              const errorMessage = actionError instanceof Error ? actionError.message : String(actionError);
              const failureCount = get().currentTask.consecutiveFailures;
              const userFriendlyError = `Action "${action.parsedAction.name}" threw an exception (${failureCount}/3): ${
                errorMessage.length > 100 ? errorMessage.substring(0, 100) + '...' : errorMessage
              }`;
              onError(userFriendlyError);
            }
            
            // Add error entry to history for AI context
            set((state) => {
              state.currentTask.history.push({
                prompt: '',
                response: '',
                action: { error: actionError instanceof Error ? actionError.message : String(actionError) },
                usage: null,
                timestamp: new Date().toISOString(),
                phase: 'error'
              });
            });
            
            // Continue with the loop for AI recovery (don't break)
            console.log(`Action exception occurred, continuing with AI recovery. Error: ${actionError}`);
          }

          // Validate action and update progress
          const currentProgress = get().currentTask.taskProgress;
          const actionName = 'parsedAction' in action ? action.parsedAction?.name || '' : '';
          const actionArgs = 'parsedAction' in action ? action.parsedAction?.args || {} : {};
          
          const validationResult = validateTaskAction(
            actionName,
            actionArgs,
            currentProgress.validationRules || {
              successIndicators: [],
              failureIndicators: [],
              pendingIndicators: []
            },
            {
              completed: currentProgress.completed,
              total: currentProgress.total
            }
          );

          set((state) => {
            state.currentTask.taskProgress = {
              ...state.currentTask.taskProgress,
              ...validationResult
            };
          });

          // No artificial delay needed - we wait for actual completion
        }
      } catch (error: any) {
        console.error('Task execution error:', error);
        if (onError) {
          onError(error.message || 'Unknown error occurred');
        }
        set((state) => {
          state.currentTask.status = 'error';
        });
      } finally {
        // Reset action status if not already set by error handling
        if (get().currentTask.status !== 'error') {
          setActionStatus('idle');
        }
      }
    },
    updateTaskProgress: (progress) => {
      set((state) => {
        state.currentTask.taskProgress = {
          ...state.currentTask.taskProgress,
          ...progress,
        };
      });
    },
    validateAction: (actionType, result) => {
      const rules = get().currentTask.taskProgress.validationRules;
      if (!rules) return 'success';
      
      const { successIndicators, failureIndicators, pendingIndicators } = rules;
      
      // Convert result to string for comparison
      const resultStr = JSON.stringify(result).toLowerCase();
      
      if (successIndicators.some(indicator => resultStr.includes(indicator.toLowerCase()))) {
        return 'success';
      }
      if (failureIndicators.some(indicator => resultStr.includes(indicator.toLowerCase()))) {
        return 'failure';
      }
      if (pendingIndicators.some(indicator => resultStr.includes(indicator.toLowerCase()))) {
        return 'pending';
      }
      
      return 'success';
    },
    interrupt: () => {
      set((state) => {
        state.currentTask.status = 'idle';
        state.currentTask.actionStatus = 'idle';
      });
    },
    clearHistory: () => {
      set((state) => {
        state.currentTask.history = [];
        state.currentTask.consecutiveFailures = 0;
        state.currentTask.lastActionResult = null;
      });
    },
  },
});
