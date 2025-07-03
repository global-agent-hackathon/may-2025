export interface ModelConfig {
  maxTokens: number;
  additionalConfig?: Record<string, any>;
}

export interface Provider {
  id: string;
  name: string;
  displayName: string;
  baseURL?: string;
  apiKeyPlaceholder: string;
  apiKeyUrl: string;
  description?: string;
  models: Record<string, ModelConfig>;
}

export const PROVIDERS: Record<string, Provider> = {
  localhost: {
    id: 'localhost',
    name: 'localhost',
    displayName: 'Ango x Gemeni Server',
    baseURL: 'http://localhost:7777',
    apiKeyPlaceholder: '',
    apiKeyUrl: '',
    description: 'Local AI server running on port 7777 (no API key required)',
    models: {
      'local-model': { maxTokens: 4096 }
    }
  },
  openai: {
    id: 'openai',
    name: 'openai',
    displayName: 'OpenAI',
    apiKeyPlaceholder: 'sk-...',
    apiKeyUrl: 'https://platform.openai.com/account/api-keys',
    description: 'Official OpenAI models',
    models: {
      'gpt-4o': { maxTokens: 2048 },
      'gpt-4o-mini': { maxTokens: 1024 },
      'o1': { maxTokens: 1024, additionalConfig: { reasoning_effort: 'low' } }
    }
  },
  openrouter: {
    id: 'openrouter',
    name: 'openrouter',
    displayName: 'OpenRouter',
    baseURL: 'https://openrouter.ai/api/v1',
    apiKeyPlaceholder: 'sk-or-...',
    apiKeyUrl: 'https://openrouter.ai/keys',
    description: 'Official OpenRouter models',
    models: {
      'google/gemini-2.0-flash-001': { maxTokens: 2048 },
      'google/gemini-2.5-flash-preview-05-20': { maxTokens: 2048 },
      'openai/gpt-4.1': { maxTokens: 4096 },
      'openai/gpt-4.1-mini': { maxTokens: 2048 },
      'meta-llama/llama-4-maverick': { maxTokens: 2048 },
      'anthropic/claude-3.7-sonnet': { maxTokens: 4096 }
    }
  }
};

// Helper functions
export const getProviderByModel = (modelId: string): Provider | undefined => {
  return Object.values(PROVIDERS).find(provider => 
    Object.keys(provider.models).includes(modelId)
  );
};

export const getModelConfig = (modelId: string): ModelConfig | undefined => {
  const provider = getProviderByModel(modelId);
  return provider?.models[modelId];
};

export const getConfiguredProviders = (apiKeys: Record<string, string | null>): Provider[] => {
  return Object.values(PROVIDERS).filter(provider => {
    // Localhost provider doesn't require an API key
    if (provider.id === 'localhost') {
      return true;
    }
    // Other providers require valid API keys
    return apiKeys[provider.id] && apiKeys[provider.id]?.trim();
  });
};

export const getAvailableModels = (apiKeys: Record<string, string | null>): Record<string, string[]> => {
  const configuredProviders = getConfiguredProviders(apiKeys);
  const modelsByProvider: Record<string, string[]> = {};
  
  configuredProviders.forEach(provider => {
    modelsByProvider[provider.id] = Object.keys(provider.models);
  });
  
  return modelsByProvider;
};

export const hasAnyApiKey = (apiKeys: Record<string, string | null>): boolean => {
  // Check if any provider has a valid API key
  return Object.values(apiKeys).some(key => key && key.trim());
};

export const hasValidProvider = (apiKeys: Record<string, string | null>, selectedModel?: string, localhostConnected?: boolean): boolean => {
  // If localhost model is selected and localhost is connected, it's valid
  if (selectedModel === 'local-model' && localhostConnected) {
    return true;
  }
  // Otherwise, check if any provider has a valid API key
  return hasAnyApiKey(apiKeys);
};

export const getFriendlyModelName = (modelId: string): string => {
  const modelMap: Record<string, string> = {
    'google/gemini-2.0-flash-001': 'Gemini 2.0 Flash',
    'google/gemini-2.5-flash-preview-05-20': 'Gemini 2.5 Flash Preview',
    'anthropic/claude-3.7-sonnet': 'Claude 3.7 Sonnet',
    'openai/gpt-4.1': 'GPT-4.1',
    'openai/gpt-4.1-mini': 'GPT-4.1 mini',
    'meta-llama/llama-4-maverick': 'Llama 4 Maverick',
    'gpt-4o': 'GPT-4o',
    'gpt-4o-mini': 'GPT-4o mini',
    'o1': 'OpenAI o1',
    'local-model': 'Local Model'
  };
  return modelMap[modelId] || modelId;
}; 