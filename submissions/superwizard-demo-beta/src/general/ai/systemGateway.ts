import OpenAI from 'openai';
import { useAppState } from '../../state/store';
import { ParsedResponseSuccess } from './parseResponse';
import { systemMessage } from './systemPrompt';
import { formatPrompt } from './formatPrompt';
import { getProviderByModel, getModelConfig } from '../providers/config';

// Define usage metrics interface
interface UsageMetrics {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

// Define action response interface
interface ActionResponse {
  thought: string;
  action: string;
  steps: string;
  validator: string;
  usage: UsageMetrics | null;
  fullPrompt?: string;
}

export async function determineNextAction(
  taskInstructions: string,
  previousActions: ParsedResponseSuccess[],
  simplifiedDOM: string,
  maxAttempts = 3,
  notifyError?: (error: string) => void
): Promise<ActionResponse | null> {
  const state = useAppState.getState();
  const { selectedModel: model, apiKeys } = state.settings;
  const allHistory = state.currentTask.history;
  
  const prompt = await formatPrompt(taskInstructions, previousActions, simplifiedDOM, allHistory);
  
  // Get provider and model configuration
  const provider = getProviderByModel(model);
  const modelConfig = getModelConfig(model);
  
  if (!provider) {
    const message = `Unknown model: ${model}`;
    notifyError?.(message);
    return null;
  }

  // Check if we have the required API key (localhost doesn't need one)
  const apiKey = apiKeys[provider.id];
  if (provider.id !== 'localhost' && (!apiKey || !apiKey.trim())) {
    const message = `No ${provider.displayName} API key found`;
    notifyError?.(message);
    return null;
  }

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      let completion: any;

      // Handle localhost server with custom API
      if (provider.id === 'localhost') {
        // First check if server is running
        try {
          const healthResponse = await fetch('http://localhost:7777/health');
          if (!healthResponse.ok) {
            throw new Error('Server health check failed');
          }
        } catch (healthError) {
          throw new Error('Cannot connect to localhost server. Please ensure your server is running on port 7777.');
        }

        // Create FormData for the localhost server
        const formData = new FormData();
        const fullPrompt = `${systemMessage}\n\nUser: ${prompt}`;
        formData.append('message', fullPrompt);
        formData.append('stream', 'false');
        formData.append('user_id', 'superwizard-extension-' + Date.now());

        const response = await fetch('http://localhost:7777/v1/playground/agents/superwizard_dom_agent/runs', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error(`Localhost server error: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();
        
        // Transform localhost response to match OpenAI format
        let content = '';
        if (data && data.content) {
          content = data.content;
        } else if (data && data.messages && data.messages.length > 0) {
          const lastMessage = data.messages[data.messages.length - 1];
          content = lastMessage.content || lastMessage.text || '';
        } else if (data && typeof data === 'string') {
          content = data;
        } else {
          throw new Error('Unexpected response format from localhost server');
        }

        completion = {
          choices: [{
            message: {
              content: content
            }
          }],
          usage: null // Localhost doesn't provide usage metrics
        };
      } else {
        // Use OpenAI client for other providers
        const openai = new OpenAI({
          apiKey: apiKey || '',
          baseURL: provider.baseURL,
          dangerouslyAllowBrowser: true,
        });

        // Prepare request config
        const requestConfig = {
          model,
          messages: [
            { role: 'system', content: systemMessage },
            { role: 'user', content: prompt }
          ],
          max_tokens: modelConfig?.maxTokens || 1024,
          temperature: 0,
          ...(modelConfig?.additionalConfig || {})
        };
        
        // Add OpenRouter specific headers if needed
        const requestOptions = provider.baseURL ? {
          headers: {
            'HTTP-Referer': 'https://github.com/amirulhamizan12/superwizard-ai',
            'X-Title': 'Browser Extension AI Assistant'
          }
        } : undefined;
        
        completion = await openai.chat.completions.create(requestConfig as any, requestOptions);
      }

      if (!completion?.choices?.[0]?.message?.content) {
        throw new Error('No response content received from AI');
      }

      // Parse response
      const response = completion.choices[0].message.content.trim();
      
      // Extract tags from response
      function extractTag(tag: string): string {
        const regex = new RegExp(`<${tag}>([\\\s\\\S]*?)<\\/${tag}>`);
        const match = response.match(regex);
        return match ? match[1].trim() : '';
      }
      
      const thought = extractTag('Thought');
      const action = extractTag('Action');
      const steps = extractTag('Steps');
      const validator = extractTag('Validator');
      
      if (!thought || !action) {
        if (attempt === maxAttempts - 1) {
          throw new Error('Invalid response format: Missing required Thought or Action tags');
        }
        continue;
      }

      // Extract usage metrics if available
      const usage = completion.usage ? {
        prompt_tokens: completion.usage.prompt_tokens,
        completion_tokens: completion.usage.completion_tokens,
        total_tokens: completion.usage.total_tokens
      } : null;

      return { thought, action, steps, validator, usage, fullPrompt: prompt };

    } catch (error) {
      console.error(`Attempt ${attempt + 1} failed:`, error);
      
      if (attempt === maxAttempts - 1) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        notifyError?.(errorMessage);
        return null;
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
    }
  }

  return null;
}
