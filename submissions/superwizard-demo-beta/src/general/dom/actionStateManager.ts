/**
 * actionStateManager.ts
 * 
 * Global action state manager for tracking DOM action completion
 * Provides event-driven action completion instead of relying on timeouts
 */

import type { ActionState, ActionCompletionCallback } from './Operation/types';

class ActionStateManager {
  private actionStates = new Map<string, ActionState>();
  private completionCallbacks = new Map<string, ActionCompletionCallback[]>();
  private activeAction: string | null = null;

  /**
   * Start tracking a new action
   */
  startAction(actionId: string, type: string): void {
    const actionState: ActionState = {
      id: actionId,
      type: type as any,
      status: 'pending',
      startTime: Date.now()
    };

    this.actionStates.set(actionId, actionState);
    this.activeAction = actionId;

    console.log(`Action started: ${type} (${actionId})`);
  }

  /**
   * Mark action as in progress
   */
  setActionInProgress(actionId: string): void {
    const state = this.actionStates.get(actionId);
    if (state) {
      state.status = 'in-progress';
      this.actionStates.set(actionId, state);
      console.log(`Action in progress: ${state.type} (${actionId})`);
    }
  }

  /**
   * Complete an action successfully
   */
  completeAction(actionId: string, details?: any): void {
    const state = this.actionStates.get(actionId);
    if (state) {
      state.status = 'completed';
      state.endTime = Date.now();
      this.actionStates.set(actionId, state);

      // Clear active action if this was it
      if (this.activeAction === actionId) {
        this.activeAction = null;
      }

      console.log(`Action completed: ${state.type} (${actionId}) in ${state.endTime - state.startTime}ms`);

      // Notify all callbacks
      this.notifyCallbacks(actionId, true);
    }
  }

  /**
   * Fail an action
   */
  failAction(actionId: string, error: string): void {
    const state = this.actionStates.get(actionId);
    if (state) {
      state.status = 'failed';
      state.endTime = Date.now();
      state.error = error;
      this.actionStates.set(actionId, state);

      // Clear active action if this was it
      if (this.activeAction === actionId) {
        this.activeAction = null;
      }

      console.log(`Action failed: ${state.type} (${actionId}) - ${error}`);

      // Notify all callbacks
      this.notifyCallbacks(actionId, false, error);
    }
  }

  /**
   * Register a callback to be called when action completes
   */
  onActionComplete(actionId: string, callback: ActionCompletionCallback): void {
    if (!this.completionCallbacks.has(actionId)) {
      this.completionCallbacks.set(actionId, []);
    }
    this.completionCallbacks.get(actionId)!.push(callback);
  }

  /**
   * Wait for an action to complete
   */
  waitForAction(actionId: string): Promise<boolean> {
    return new Promise((resolve) => {
      const state = this.actionStates.get(actionId);
      
      // If action is already completed or failed, resolve immediately
      if (state && (state.status === 'completed' || state.status === 'failed')) {
        resolve(state.status === 'completed');
        return;
      }

      // Otherwise, wait for completion
      this.onActionComplete(actionId, (success) => {
        resolve(success);
      });
    });
  }

  /**
   * Check if any action is currently active
   */
  hasActiveAction(): boolean {
    return this.activeAction !== null;
  }

  /**
   * Get the current active action ID
   */
  getActiveActionId(): string | null {
    return this.activeAction;
  }

  /**
   * Wait for all actions to complete
   */
  waitForAllActions(): Promise<void> {
    return new Promise((resolve) => {
      const checkComplete = () => {
        if (!this.hasActiveAction()) {
          resolve();
          return;
        }
        // Check again in 50ms
        setTimeout(checkComplete, 50);
      };
      checkComplete();
    });
  }

  /**
   * Get action state
   */
  getActionState(actionId: string): ActionState | undefined {
    return this.actionStates.get(actionId);
  }

  /**
   * Clean up old completed actions (keep last 10)
   */
  cleanup(): void {
    const states = Array.from(this.actionStates.entries());
    const completed = states.filter(([_, state]) => 
      state.status === 'completed' || state.status === 'failed'
    );

    if (completed.length > 10) {
      // Remove oldest completed actions
      const toRemove = completed
        .sort(([_, a], [__, b]) => (a.endTime || 0) - (b.endTime || 0))
        .slice(0, completed.length - 10);

      toRemove.forEach(([actionId]) => {
        this.actionStates.delete(actionId);
        this.completionCallbacks.delete(actionId);
      });
    }
  }

  /**
   * Notify all callbacks for an action
   */
  private notifyCallbacks(actionId: string, success: boolean, error?: string): void {
    const callbacks = this.completionCallbacks.get(actionId);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(success, error);
        } catch (err) {
          console.error('Error in action completion callback:', err);
        }
      });
      
      // Clean up callbacks after notifying
      this.completionCallbacks.delete(actionId);
    }
  }
}

// Global singleton instance
export const actionStateManager = new ActionStateManager(); 