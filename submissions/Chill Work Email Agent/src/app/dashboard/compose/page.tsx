'use client';

import { useState, FormEvent } from 'react';
import { Sparkles, Send, X, AlertTriangle, CheckCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ComposeMail() {
    const [toAddress, setToAddress] = useState('');
    const [subject, setSubject] = useState('');
    const [contentPlain, setContentPlain] = useState('');
    const [isSending, setIsSending] = useState(false); // For the "Send" button
    const [isGenerating, setIsGenerating] = useState(false); // For the "Generate" button
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [userPromptForDraft, setUserPromptForDraft] = useState(''); // Optional: a small input for user prompt

    const router = useRouter();

    const handleClose = () => router.back();

    const handleSubmitEmail = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsSending(true);
        setError(null);
        setSuccessMessage(null);
        try {
            const response = await fetch(`${API_BASE_URL}/api/mails/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    to_address: toAddress,
                    subject: subject,
                    content_plain: contentPlain,
                }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Failed to send email.');
            setSuccessMessage(result.message || 'Email sent successfully!');
            // Reset form, navigate, etc.
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsSending(false);
        }
    };

    const handleGenerateWithAI = async () => {
        if (!toAddress && !userPromptForDraft) {
            setError("Please provide a recipient or a prompt for the AI to generate content.");
            return;
        }
        setIsGenerating(true);
        setError(null);
        setSuccessMessage(null);
        try {
            // Simple prompt: what the user wants to achieve with the email.
            // Can be a dedicated input field or derived.
            let prompt = userPromptForDraft || `Write an email to ${toAddress}`;
            if (subject && !userPromptForDraft) prompt += ` about ${subject}`;


            const response = await fetch(`${API_BASE_URL}/api/agents/writing/draft`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    recipient_to: toAddress,
                    user_prompt: prompt, // User's goal for the email
                    current_draft_content: contentPlain // Pass current content if any
                }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Failed to generate draft.');

            setSubject(result.subject || subject); // Update subject if AI provided one
            setContentPlain(result.body || contentPlain); // Update body
            setSuccessMessage("AI drafted content successfully!");

        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="bg-zinc-900 rounded-lg shadow-md w-full max-w-2xl mx-auto min-h-[calc(100vh-4rem)] flex flex-col">
            <div className="flex justify-between items-center p-4 border-b border-zinc-700">
                <h2 className="text-base font-medium text-zinc-100">Compose Mail</h2>
                <button
                    onClick={handleClose}
                    className="text-zinc-500 hover:text-zinc-100 p-2 rounded-full hover:bg-zinc-700 transition-colors"
                    aria-label="Close compose window"
                >
                    <X size={18} />
                </button>
            </div>

            <form onSubmit={handleSubmitEmail} className="flex-1 p-4 space-y-4">
                <div>
                    <label
                        htmlFor="userPromptForDraft"
                        className="block text-sm font-medium text-zinc-100 mb-1"
                    >
                        AI Draft Prompt (optional)
                    </label>
                    <input
                        id="userPromptForDraft"
                        type="text"
                        placeholder="e.g., Follow up on last week's meeting about project X"
                        value={userPromptForDraft}
                        onChange={(e) => setUserPromptForDraft(e.target.value)}
                        className="w-full p-3 bg-zinc-700 text-zinc-100 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-zinc-500 focus:border-zinc-500 outline-none text-sm placeholder-zinc-500"
                        aria-describedby="userPromptForDraft-hint"
                    />
                    <p
                        id="userPromptForDraft-hint"
                        className="text-xs text-zinc-500 mt-1"
                    >
                        Provide guidance for AI to draft your email.
                    </p>
                </div>

                <div>
                    <label
                        htmlFor="toAddress"
                        className="block text-sm font-medium text-zinc-100 mb-1"
                    >
                        To
                    </label>
                    <input
                        id="toAddress"
                        type="email"
                        placeholder="recipient@example.com"
                        value={toAddress}
                        onChange={(e) => setToAddress(e.target.value)}
                        required
                        className="w-full p-3 bg-zinc-700 text-zinc-100 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-zinc-500 focus:border-zinc-500 outline-none text-sm placeholder-zinc-500"
                        aria-required="true"
                    />
                </div>

                <div>
                    <label
                        htmlFor="subject"
                        className="block text-sm font-medium text-zinc-100 mb-1"
                    >
                        Subject
                    </label>
                    <input
                        id="subject"
                        type="text"
                        placeholder="Subject of your email"
                        value={subject}
                        onChange={(e) => setSubject(e.target.value)}
                        required
                        className="w-full p-3 bg-zinc-700 text-zinc-100 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-zinc-500 focus:border-zinc-500 outline-none text-sm placeholder-zinc-500"
                        aria-required="true"
                    />
                </div>

                <div>
                    <label
                        htmlFor="contentPlain"
                        className="block text-sm font-medium text-zinc-100 mb-1"
                    >
                        Content
                    </label>
                    <textarea
                        id="contentPlain"
                        placeholder="Write your message here..."
                        rows={8}
                        value={contentPlain}
                        onChange={(e) => setContentPlain(e.target.value)}
                        required
                        className="w-full p-3 bg-zinc-700 text-zinc-100 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-zinc-500 focus:border-zinc-500 outline-none resize-y text-sm placeholder-zinc-500 scrollbar-thin scrollbar-thumb-zinc-500 scrollbar-track-zinc-900"
                        aria-required="true"
                    />
                </div>

                {(error || successMessage) && (
                    <div className="py-2">
                        {error && (
                            <p className="text-red-500 text-sm flex items-center gap-1.5">
                                <AlertTriangle size={14} /> {error}
                            </p>
                        )}
                        {successMessage && !error && (
                            <p className="text-green-500 text-sm flex items-center gap-1.5">
                                <CheckCircle size={14} /> {successMessage}
                            </p>
                        )}
                    </div>
                )}

                <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-zinc-700">
                    <button
                        type="button"
                        onClick={handleGenerateWithAI}
                        disabled={isGenerating || isSending}
                        className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-zinc-500 text-zinc-100 rounded-lg hover:bg-zinc-700 focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2 focus:ring-offset-zinc-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                    >
                        {isGenerating ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-zinc-100"></div>
                        ) : (
                            <Sparkles size={16} />
                        )}
                        <span>{isGenerating ? 'Generating...' : 'Generate with AI'}</span>
                    </button>
                    <button
                        type="submit"
                        disabled={isSending || isGenerating || !toAddress || !subject || !contentPlain}
                        className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-zinc-500 text-zinc-100 rounded-lg hover:bg-zinc-700 focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2 focus:ring-offset-zinc-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                    >
                        {isSending ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-zinc-100"></div>
                        ) : (
                            <Send size={16} />
                        )}
                        <span>{isSending ? 'Sending...' : 'Send'}</span>
                    </button>
                </div>
            </form>
        </div>
    );
}