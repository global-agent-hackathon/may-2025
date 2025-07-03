import { MyStateCreator } from './store';
import { getCurrentTab } from '../general/utils/utils';
import { PROVIDERS, hasAnyApiKey } from '../general/providers/config';

// Function to update cursor settings in storage and notify content script
const syncCursorSetting = async (enabled: boolean) => {
  console.log('Syncing cursor setting:', enabled);
  
  try {
    // Save setting to Chrome storage
    await chrome.storage.sync.set({ cursorEnabled: enabled });
    console.log('Cursor setting saved to storage');
    
    // Notify any active tabs about the setting change
    const tab = await getCurrentTab();
    if (tab?.id) {
      await chrome.tabs.sendMessage(tab.id, { 
        type: 'UPDATE_CURSOR_STATE', 
        enabled 
      });
      console.log('Cursor state update sent to tab');
    } else {
      console.log('No active tab found to update cursor state');
    }
  } catch (error) {
    console.error('Failed to sync cursor setting:', error);
  }
};

// Function to load settings from Chrome storage
const loadSettings = async (set: Function) => {
  try {
    const result = await chrome.storage.sync.get(['cursorEnabled']);
    // Only update if the setting exists
    if (result.cursorEnabled !== undefined) {
      set((state: any) => {
        state.settings.cursorEnabled = result.cursorEnabled;
      });
    }
  } catch (error) {
    console.warn('Failed to load settings from storage:', error);
  }
};

export type SettingsSlice = {
  // Legacy support - will be migrated to apiKeys
  openAIKey: string | null;
  openRouterKey: string | null;
  // New provider-based system
  apiKeys: Record<string, string | null>;
  selectedModel: string;
  cursorEnabled: boolean;
  localhostConnected: boolean;
  actions: {
    update: (values: Partial<SettingsSlice>) => void;
    updateApiKey: (providerId: string, apiKey: string | null) => void;
    updateLocalhostStatus: (connected: boolean) => void;
    clearAllApiKeys: () => void;
    toggleCursor: () => void;
  };
};

export const createSettingsSlice: MyStateCreator<SettingsSlice> = (set, get) => {
  // Load settings from storage when the slice is created
  setTimeout(() => loadSettings(set), 0);
  
  return {
    // Legacy fields for backward compatibility
    openAIKey: null,
    openRouterKey: null,
    // New provider system
    apiKeys: Object.keys(PROVIDERS).reduce((acc, providerId) => {
      acc[providerId] = null;
      return acc;
    }, {} as Record<string, string | null>),
    selectedModel: 'local-model',
    cursorEnabled: true,
    localhostConnected: false,
    actions: {
      update: (values) => {
        set((state) => {
          // Handle legacy key updates and migrate to new system
          if (values.openAIKey !== undefined) {
            state.settings.openAIKey = values.openAIKey;
            state.settings.apiKeys.openai = values.openAIKey;
          }
          if (values.openRouterKey !== undefined) {
            state.settings.openRouterKey = values.openRouterKey;
            state.settings.apiKeys.openrouter = values.openRouterKey;
          }
          
          // Update other settings
          if (values.selectedModel !== undefined) {
            state.settings.selectedModel = values.selectedModel;
          }
          if (values.cursorEnabled !== undefined) {
            state.settings.cursorEnabled = values.cursorEnabled;
            syncCursorSetting(values.cursorEnabled);
          }
          if (values.apiKeys !== undefined) {
            state.settings.apiKeys = { ...state.settings.apiKeys, ...values.apiKeys };
            // Keep legacy fields in sync
            if (values.apiKeys.openai !== undefined) {
              state.settings.openAIKey = values.apiKeys.openai;
            }
            if (values.apiKeys.openrouter !== undefined) {
              state.settings.openRouterKey = values.apiKeys.openrouter;
            }
          }
        });
      },
      updateApiKey: (providerId: string, apiKey: string | null) => {
        set((state) => {
          state.settings.apiKeys[providerId] = apiKey;
          // Keep legacy fields in sync
          if (providerId === 'openai') {
            state.settings.openAIKey = apiKey;
          } else if (providerId === 'openrouter') {
            state.settings.openRouterKey = apiKey;
          }
        });
      },
      updateLocalhostStatus: (connected: boolean) => {
        set((state) => {
          state.settings.localhostConnected = connected;
        });
      },
      clearAllApiKeys: () => {
        set((state) => {
          Object.keys(state.settings.apiKeys).forEach(providerId => {
            state.settings.apiKeys[providerId] = null;
          });
          // Clear legacy fields
          state.settings.openAIKey = null;
          state.settings.openRouterKey = null;
          // Reset selected model to a non-localhost model to ensure user is redirected to SetAPIKey page
          // We'll use the first available non-localhost model
          const nonLocalhostModels = Object.values(PROVIDERS)
            .filter(provider => provider.id !== 'localhost')
            .flatMap(provider => Object.keys(provider.models));
          if (nonLocalhostModels.length > 0) {
            state.settings.selectedModel = nonLocalhostModels[0];
          }
        });
      },
      toggleCursor: () => {
        set((state) => {
          const newValue = !state.settings.cursorEnabled;
          state.settings.cursorEnabled = newValue;
          syncCursorSetting(newValue);
        });
      }
    },
  };
};
