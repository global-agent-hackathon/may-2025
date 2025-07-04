'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

export default function ChatPage() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to the latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        // Add user message to the chat
        const userMessage: ChatMessage = { role: 'user', content: query };
        setMessages((prev) => [...prev, userMessage]);
        setQuery('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/api/agents/query/chat', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: userMessage.content,
                    history: messages.map((msg) => ({
                        role: msg.role,
                        content: msg.content,
                    })),
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch response');
            }

            const data = await response.json();
            const assistantMessage: ChatMessage = { role: 'assistant', content: data.answer };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unexpected error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col min-h-screen bg-zinc-900 text-zinc-100">
            {/* Chat container */}
            <div className="flex-1 max-w-3xl mx-auto w-full p-4">
                <div className="bg-zinc-800 rounded-lg shadow-lg p-4 h-[calc(100vh-12rem)] overflow-y-auto">
                    {messages.length === 0 ? (
                        <div className="h-full flex items-center justify-center text-zinc-400">
                            Start a conversation by typing a message below.
                        </div>
                    ) : (
                        messages.map((message, index) => (
                            <div
                                key={index}
                                className={`mb-4 p-3 rounded-lg ${message.role === 'user'
                                    ? 'bg-zinc-700 ml-10 text-zinc-100'
                                    : 'bg-zinc-950 mr-10 text-zinc-200'
                                    }`}
                            >
                                <span className="font-semibold">
                                    {message.role === 'user' ? 'You: ' : 'Assistant: '}
                                </span>
                                {message.content}
                            </div>
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input form */}
            <div className="max-w-3xl mx-auto w-full p-4">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 p-3 rounded-lg bg-zinc-800 text-zinc-100 placeholder-zinc-400 border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-zinc-500 transition-colors"
                        disabled={isLoading}
                        aria-label="Chat input"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !query.trim()}
                        className="p-3 bg-zinc-700 text-zinc-100 rounded-lg hover:bg-zinc-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        aria-label="Send message"
                    >
                        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                    </button>
                </form>
                {error && (
                    <div className="mt-2 text-red-400 text-sm" role="alert">
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
}