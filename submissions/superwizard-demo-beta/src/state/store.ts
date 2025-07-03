import { merge } from 'lodash';
import { create, StateCreator } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { createJSONStorage, devtools, persist } from 'zustand/middleware';
import { createCurrentTaskSlice, CurrentTaskSlice } from './currentTask';
import { createUiSlice, UiSlice } from './ui';
import { createSettingsSlice, SettingsSlice } from './settings';

export type StoreType = {
  currentTask: CurrentTaskSlice;
  ui: UiSlice;
  settings: SettingsSlice;
};

export type MyStateCreator<T> = StateCreator<
  StoreType,
  [['zustand/immer', never]],
  [],
  T
>;

export const useAppState = create<StoreType>()(
  persist(
    immer(
      devtools((...a) => ({
        currentTask: createCurrentTaskSlice(...a),
        ui: createUiSlice(...a),
        settings: createSettingsSlice(...a),
      }))
    ),
    {
      name: 'app-state',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Stuff we want to persist
        ui: {
          instructions: state.ui.instructions,
        },
        settings: {
          // Legacy fields for backward compatibility
          openAIKey: state.settings.openAIKey,
          openRouterKey: state.settings.openRouterKey,
          // New provider system
          apiKeys: state.settings.apiKeys,
          selectedModel: state.settings.selectedModel,
        },
      }),
      merge: (persistedState: any, currentState: StoreType) => {
        const merged = merge(currentState, persistedState);
        
        // Migration logic: if we have legacy keys but not apiKeys, migrate them
        if (merged.settings && (!merged.settings.apiKeys || Object.keys(merged.settings.apiKeys).length === 0)) {
          merged.settings.apiKeys = {};
          if (merged.settings.openAIKey) {
            merged.settings.apiKeys.openai = merged.settings.openAIKey;
          }
          if (merged.settings.openRouterKey) {
            merged.settings.apiKeys.openrouter = merged.settings.openRouterKey;
          }
        }
        
        return merged;
      },
    }
  )
);

// @ts-expect-error used for debugging
window.getState = useAppState.getState;
