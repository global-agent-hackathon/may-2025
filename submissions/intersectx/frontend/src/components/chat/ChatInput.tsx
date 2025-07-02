import React, { useState } from 'react';
import type { FormEvent } from 'react';
import { cn } from '../../lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({ 
  onSend, 
  onCancel,
  isLoading = false, 
  placeholder = "Type your message..." 
}: ChatInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    
    onSend(inputValue);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.metaKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex w-full flex-1 items-stretch rounded-2xl bg-white shadow-sm border border-gray-200 focus-within:border-purple-light focus-within:ring-1 focus-within:ring-purple-light transition-all">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="form-input flex w-full min-w-0 flex-1 resize-none overflow-auto rounded-2xl text-primary focus:outline-0 focus:ring-0 border-none bg-white focus:border-none placeholder:text-secondary px-5 py-3 rounded-r-none"
          style={{
            minHeight: '2.75rem',
            maxHeight: '12rem',
            height: 'auto',
          }}
        />
        <div className="flex items-center justify-center pr-5 rounded-r-2xl bg-white">
          {isLoading ? (
            <button
              type="button"
              onClick={onCancel}
              className="min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-9 px-4 bg-gray-200 text-primary text-sm font-medium leading-normal flex gap-2 hover:bg-gray-300 transition-colors"
            >
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="truncate">Cancel</span>
            </button>
          ) : (
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className={cn(
                "min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-9 px-4 bg-purple text-white text-sm font-medium leading-normal transition-all hover:bg-purple-dark shadow-sm flex gap-1 items-center",
                !inputValue.trim() && "opacity-50 cursor-not-allowed"
              )}
            >
              <span className="truncate">Send</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m5 12 14-7-7 14v-7l-7-7"/>
              </svg>
            </button>
          )}
        </div>
      </div>
    </form>
  );
} 