'use client';

import { useState, useRef, useEffect, FormEvent, KeyboardEvent } from 'react';
import { Send, Bot, User, AlertTriangle } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'llm';
    timestamp: Date;
    isError?: boolean;
}

interface ChatHistoryItem {
    sender: 'user' | 'assistant';
    text: string;
}

export default function ChatUI() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 'initial-llm-msg',
            text: "Hello! I'm your AI assistant. How can I help you with your emails today?",
            sender: 'llm',
            timestamp: new Date(),
        },
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const messagesEndRef = useRef<null | HTMLDivElement>(null);
    const inputRef = useRef<null | HTMLTextAreaElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    // Auto-resize textarea
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.style.height = 'auto'; // Reset height
            const scrollHeight = inputRef.current.scrollHeight;
            const maxHeight = 120; // Max height in pixels for textarea (e.g., ~5 lines)
            inputRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
        }
    }, [inputValue]);

    const processSendMessage = async () => {
        const trimmedInput = inputValue.trim();
        if (!trimmedInput || isLoading) return;

        const userMessage: Message = {
            id: `${Date.now()}-user`,
            text: trimmedInput,
            sender: 'user',
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);
        setError(null); // Clear previous general errors

        // Prepare history for the backend
        const historyForBackend: ChatHistoryItem[] = messages
            .filter(msg => !msg.isError) // Exclude error messages from history
            .slice(-5) // Send last 5 non-error messages
            .map(msg => ({
                sender: msg.sender === 'llm' ? 'assistant' : 'user',
                text: msg.text
            }));

        try {
            const response = await fetch(`${API_BASE_URL}/api/agents/query/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ query: trimmedInput, history: historyForBackend }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ detail: "An unknown error occurred" }));
                throw new Error(errData.detail || `HTTP error ${response.status}`);
            }

            const result = await response.json();
            const llmResponse: Message = {
                id: `${Date.now()}-llm`,
                text: result.answer,
                sender: 'llm',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, llmResponse]);

        } catch (err: any) {
            console.error("Chat API error:", err);
            const errorResponse: Message = {
                id: `${Date.now()}-error-llm`,
                text: `Sorry, I encountered an issue: ${err.message || "Failed to get a response."}`,
                sender: 'llm',
                timestamp: new Date(),
                isError: true, // Flag this as an error message
            };
            setMessages((prev) => [...prev, errorResponse]);
        } finally {
            setIsLoading(false);
            // Slight delay to ensure UI updates before focusing
            setTimeout(() => inputRef.current?.focus(), 0);
        }
    };

    const handleFormSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        processSendMessage();
    };

    const handleTextareaKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
            e.preventDefault();
            processSendMessage();
        }
    };

    return (
        <div className="flex flex-col h-full bg-zinc-900 text-white rounded-lg shadow-lg overflow-hidden border border-zinc-700">
            {/* Header */}
            <div className="px-4 py-3 border-b border-zinc-700 flex items-center gap-2 bg-zinc-900">
                <Bot size={18} className="text-zinc-500" />
                <h2 className="text-base font-medium text-white">AI Email Assistant</h2>
            </div>

            {/* Chat messages area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-zinc-900">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex w-full items-start ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`flex items-end gap-2 max-w-[80%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
                                }`}
                        >
                            <div
                                className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-white ${msg.sender === 'llm' ? (msg.isError ? 'bg-red-600' : 'bg-zinc-700') : 'bg-zinc-500'
                                    }`}
                            >
                                {msg.sender === 'llm' ? (
                                    msg.isError ? <AlertTriangle size={16} /> : <Bot size={16} />
                                ) : (
                                    <User size={16} />
                                )}
                            </div>
                            <div
                                className={`px-3 py-2 rounded-lg shadow-sm ${msg.sender === 'user'
                                        ? 'bg-zinc-500 text-white rounded-br-none'
                                        : msg.isError
                                            ? 'bg-red-600 border border-red-500 text-white rounded-bl-none'
                                            : 'bg-zinc-700 text-white rounded-bl-none'
                                    }`}
                            >
                                <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">
                                    {msg.text}
                                </p>
                                <p
                                    className={`text-xs mt-1 opacity-80 ${msg.sender === 'user' ? 'text-right' : 'text-left'
                                        }`}
                                >
                                    {msg.timestamp.toLocaleTimeString([], {
                                        hour: 'numeric',
                                        minute: '2-digit',
                                        hour12: true,
                                    })}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <div className="px-4 py-3 border-t border-zinc-700 bg-zinc-900">
                <form onSubmit={handleFormSubmit} className="flex items-center gap-2">
                    <textarea
                        ref={inputRef}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleTextareaKeyDown}
                        placeholder={isLoading ? 'AI is thinking...' : 'Ask about your emails...'}
                        className="flex-1 p-2 bg-zinc-700 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-zinc-500 focus:border-zinc-500 focus:outline-none text-white placeholder-zinc-500 resize-none text-sm leading-relaxed min-h-[40px] max-h-[100px] scrollbar-thin scrollbar-thumb-zinc-500 scrollbar-track-zinc-900"
                        rows={1}
                        disabled={isLoading}
                        aria-label="Chat input"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !inputValue.trim()}
                        className="p-2 bg-zinc-500 hover:bg-zinc-700 focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2 focus:ring-offset-zinc-900 disabled:bg-zinc-700 disabled:text-zinc-500 disabled:cursor-not-allowed rounded-lg text-white flex items-center justify-center h-10 w-10 transition-colors duration-150"
                        aria-label="Send message"
                    >
                        {isLoading ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-zinc-900 border-t-white"></div>
                        ) : (
                            <Send size={18} />
                        )}
                    </button>
                </form>
                {!isLoading && (
                    <p className="text-xs text-zinc-500 mt-2 text-center">
                        Shift+Enter for new line. Enter to send.
                    </p>
                )}
            </div>
        </div>
    );
}