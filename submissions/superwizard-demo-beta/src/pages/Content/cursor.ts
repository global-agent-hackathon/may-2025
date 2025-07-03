/**
 * Cursor Simulator for SuperWizard
 * Creates a visual cursor that moves to elements before interactions.
 */

interface CursorOptions {
  size?: number;
  color?: string;
  zIndex?: number;
  transitionDuration?: number;
  clickAnimationDuration?: number;
}

export class CursorSimulator {
  private container: HTMLDivElement | null = null;
  private cursor: HTMLDivElement | null = null;
  private clickRipple: HTMLDivElement | null = null;
  private currentX: number = 0;
  private currentY: number = 0;
  private isMoving: boolean = false;
  private options: Required<CursorOptions>;
  
  constructor(options: CursorOptions = {}) {
    this.options = {
      size: options.size || 16,
      color: options.color || '#5C7CFA',
      zIndex: options.zIndex || 9999,
      transitionDuration: options.transitionDuration || 500,
      clickAnimationDuration: options.clickAnimationDuration || 300
    };
  }
  
  /**
   * Initialize the cursor in the DOM
   */
  public initialize(): void {
    if (this.container) {
      if (!document.body.contains(this.container)) {
        document.body.appendChild(this.container);
      }
      if (this.cursor) {
        this.cursor.style.opacity = '0.9';
      }
      return;
    }
    
    this.container = document.createElement('div');
    this.container.id = 'superwizard-cursor-container';
    Object.assign(this.container.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      zIndex: `${this.options.zIndex}`
    });
    
    this.cursor = document.createElement('div');
    this.cursor.id = 'superwizard-cursor';
    Object.assign(this.cursor.style, {
      position: 'absolute',
      width: `${this.options.size}px`,
      height: `${this.options.size}px`,
      borderRadius: '50%',
      backgroundColor: this.options.color,
      boxShadow: `0 0 0 1px rgba(255, 255, 255, 0.8), 0 0 5px rgba(0, 0, 0, 0.3)`,
      transform: 'translate(-50%, -50%)',
      transition: 'opacity 0.2s ease',
      opacity: '0.9'
    });
    
    this.clickRipple = document.createElement('div');
    this.clickRipple.id = 'superwizard-cursor-ripple';
    Object.assign(this.clickRipple.style, {
      position: 'absolute',
      width: `${this.options.size}px`,
      height: `${this.options.size}px`,
      borderRadius: '50%',
      backgroundColor: 'transparent',
      border: `2px solid ${this.options.color}`,
      transform: 'translate(-50%, -50%) scale(1)',
      opacity: '0'
    });
    
    this.container.appendChild(this.cursor);
    this.container.appendChild(this.clickRipple);
    document.body.appendChild(this.container);
    
    this.currentX = window.innerWidth / 2;
    this.currentY = window.innerHeight / 2;
    this.updateCursorPosition(this.currentX, this.currentY);
  }
  
  /**
   * Destroy the cursor and clean up
   */
  public destroy(): void {
    if (this.container) {
      this.container.remove();
      this.container = null;
      this.cursor = null;
      this.clickRipple = null;
    }
  }
  
  /**
   * Move cursor to specified coordinates with animation
   */
  public async moveTo(x: number, y: number, duration: number = this.options.transitionDuration): Promise<void> {
    if (!this.cursor || (this.currentX === x && this.currentY === y)) return;
    
    this.cursor.style.transition = `left ${duration}ms ease-in-out, top ${duration}ms ease-in-out`;
    this.updateCursorPosition(x, y);
    
    return new Promise(resolve => {
      this.isMoving = true;
      setTimeout(() => {
        this.isMoving = false;
        resolve();
      }, duration);
    });
  }
  
  /**
   * Move cursor to an element (centered on the element)
   */
  public async moveToElement(element: HTMLElement, duration: number = this.options.transitionDuration): Promise<void> {
    await this.scrollElementIntoView(element);
    const rect = element.getBoundingClientRect();
    return this.moveTo(rect.left + rect.width / 2, rect.top + rect.height / 2, duration);
  }
  
  /**
   * Scroll an element into view if needed
   */
  private async scrollElementIntoView(element: HTMLElement): Promise<void> {
    const rect = element.getBoundingClientRect();
    const inView = (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= window.innerHeight &&
      rect.right <= window.innerWidth
    );
    
    if (!inView) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return new Promise(resolve => setTimeout(resolve, 500));
    }
    return Promise.resolve();
  }
  
  /**
   * Move cursor to coordinates immediately without animation
   */
  public moveToAbsolute(x: number, y: number, delay: number = 0): Promise<void> {
    if (!this.cursor) return Promise.resolve();
    this.cursor.style.transition = 'none';
    this.updateCursorPosition(x, y);
    return delay ? new Promise(resolve => setTimeout(resolve, delay)) : Promise.resolve();
  }
  
  /**
   * Simulate a click animation at the current cursor position
   */
  public async click(animationDuration: number = this.options.clickAnimationDuration): Promise<void> {
    if (!this.clickRipple || !this.cursor) return Promise.resolve();
    
    this.clickRipple.style.left = `${this.currentX}px`;
    this.clickRipple.style.top = `${this.currentY}px`;
    this.cursor.style.transform = 'translate(-50%, -50%) scale(0.8)';
    
    this.clickRipple.style.transition = `transform ${animationDuration}ms ease-out, opacity ${animationDuration}ms ease-out`;
    this.clickRipple.style.opacity = '0.6';
    this.clickRipple.style.transform = 'translate(-50%, -50%) scale(2.5)';
    
    return new Promise(resolve => {
      setTimeout(() => {
        if (this.cursor) {
          this.cursor.style.transform = 'translate(-50%, -50%)';
        }
        if (this.clickRipple) {
          this.clickRipple.style.opacity = '0';
          this.clickRipple.style.transform = 'translate(-50%, -50%) scale(1)';
        }
        resolve();
      }, animationDuration);
    });
  }
  
  /**
   * Simulate typing animation (pulse cursor)
   */
  public async simulateTyping(duration: number = 500): Promise<void> {
    // No animation, just immediately resolve
    return Promise.resolve();
  }
  
  /**
   * Update the cursor position
   */
  private updateCursorPosition(x: number, y: number): void {
    if (!this.cursor) return;
    this.currentX = x;
    this.currentY = y;
    this.cursor.style.left = `${x}px`;
    this.cursor.style.top = `${y}px`;
  }
  
  /**
   * Get the current cursor position
   */
  public getCurrentPosition(): { x: number; y: number } {
    return { x: this.currentX, y: this.currentY };
  }
  
  /**
   * Check if cursor is currently moving
   */
  public isCurrentlyMoving(): boolean {
    return this.isMoving;
  }
}

/**
 * Integration helper to connect with DOM actions
 */
export const initCursorIntegration = () => {
  const cursor = new CursorSimulator();
  cursor.initialize();
  
  (window as any).__superwizardCursor = cursor;
  
  return {
    beforeClick: async (elementId: number, getElementFn: (id: number) => Promise<HTMLElement>): Promise<void> => {
      try {
        const element = await getElementFn(elementId);
        if (element) {
          await cursor.moveToElement(element);
          await cursor.click();
        }
      } catch (error) {
        console.warn('Cursor pre-click movement failed:', error);
      }
    },
    
    beforeSetValue: async (elementId: number, getElementFn: (id: number) => Promise<HTMLElement>): Promise<void> => {
      try {
        const element = await getElementFn(elementId);
        if (element) {
          await cursor.moveToElement(element);
        }
      } catch (error) {
        console.warn('Cursor pre-setValue movement failed:', error);
      }
    },
    
    getCursor: () => cursor
  };
};

// Make CursorSimulator available globally
(window as any).CursorSimulator = CursorSimulator;
