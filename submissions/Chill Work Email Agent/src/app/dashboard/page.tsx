'use client';

import { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Info, Loader2, Mail } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface SyncResponse {
    message: string;
    newly_synced_to_db: number;
    updated_in_db: number;
    failed_to_parse: number;
    ai_categorization_failed: number;
    gmail_api_errors_during_fetch: number;
    mem0_memories_added: number;
    mem0_memories_failed: number;
    total_message_ids_considered: number;
}

interface DailySummary {
    summary: string;
    generated_at: string; // ISO date string
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function DashboardPage() {
    const [syncStatus, setSyncStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [syncData, setSyncData] = useState<SyncResponse | null>(null);
    const [syncError, setSyncError] = useState<string | null>(null);

    const [summary, setSummary] = useState<string | null>(null);
    const [summaryStatus, setSummaryStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [summaryError, setSummaryError] = useState<string | null>(null);
    const [summaryGeneratedAt, setSummaryGeneratedAt] = useState<string | null>(null);

    const handleSyncMails = async () => {
        setSyncStatus('loading');
        setSyncData(null);
        setSyncError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/api/sync-mails`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            setSyncData(data as SyncResponse);
            setSyncStatus('success');
            // After successful sync, fetch the new summary
            fetchDailySummary();
        } catch (error: any) {
            setSyncError(error.message || 'An unknown error occurred during sync.');
            setSyncStatus('error');
        }
    };

    const fetchDailySummary = async () => {
        setSummaryStatus('loading');
        setSummary(null);
        setSummaryError(null);
        setSummaryGeneratedAt(null);
        try {
            const response = await fetch(`${API_BASE_URL}/api/agents/summary/daily`, {
                method: 'GET',
                credentials: 'include',
            });
            const data: DailySummary = await response.json();
            if (!response.ok) throw new Error((data as any).detail || `HTTP error! status: ${response.status}`);
            setSummary(data.summary);
            setSummaryGeneratedAt(data.generated_at);
            setSummaryStatus('success');
        } catch (error: any) {
            setSummaryError(error.message || 'Failed to load daily summary.');
            setSummaryStatus('error');
        }
    };

    useEffect(() => {
        // Fetch summary on initial page load
        fetchDailySummary();
        handleSyncMails();
    }, []);

    return (
        <div className="min-h-screen bg-zinc-950 text-zinc-100 p-4 md:p-8 space-y-8">
            <header className="pb-2 border-b border-zinc-800">
                <h1 className="text-3xl font-bold text-white">Dashboard</h1>
            </header>

            {/* Sync Mails Section */}
            <section className="p-6 bg-zinc-900 rounded-xl shadow-lg border border-zinc-800">
                <h2 className="text-2xl font-semibold text-white mb-4">Mail Synchronization</h2>
                <button
                    onClick={handleSyncMails}
                    disabled={syncStatus === 'loading'}
                    className="px-6 py-3 bg-zinc-600 hover:bg-zinc-500 focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2 focus:ring-offset-zinc-900 text-white font-semibold rounded-lg shadow-md disabled:opacity-60 disabled:cursor-not-allowed transition duration-150 ease-in-out flex items-center gap-2"
                >
                    {syncStatus === 'loading' ? (
                        <Loader2 className="animate-spin" size={20} />
                    ) : (
                        <Mail size={20} />
                    )}
                    {syncStatus === 'loading' ? 'Syncing Mails...' : 'Sync Mails Now'}
                </button>

                {syncStatus === 'loading' && (
                    <p className="mt-4 text-sm text-blue-400 flex items-center gap-2">
                        <Loader2 className="animate-spin" size={16} />
                        Syncing in progress...
                    </p>
                )}
                {syncStatus === 'error' && syncError && (
                    <div className="mt-4 p-4 bg-red-900 border border-red-700 text-red-200 rounded-lg flex items-start gap-3">
                        <AlertTriangle size={20} className="text-red-400 mt-0.5 flex-shrink-0" />
                        <div>
                            <h3 className="font-semibold">Sync Error:</h3>
                            <p className="text-sm">{syncError}</p>
                        </div>
                    </div>
                )}
                {syncStatus === 'success' && syncData && (
                    <div className="mt-4 p-4 bg-zinc-900 border border-green-700 text-green-200 rounded-lg flex items-start gap-3">
                        <CheckCircle size={20} className="text-green-400 mt-0.5 flex-shrink-0" />
                        <div>
                            <h3 className="font-semibold">Sync Successful</h3>
                        </div>
                    </div>
                )}
            </section>

            {/* Daily Summary Card */}
            <section className="p-6 bg-zinc-900 rounded-xl shadow-lg border border-zinc-800">
                <h2 className="text-2xl font-semibold text-white mb-4">Today's Email Summary</h2>
                {summaryStatus === 'loading' && (
                    <div className="flex items-center gap-2 text-zinc-400">
                        <Loader2 className="animate-spin" size={20} />
                        <span>Loading summary...</span>
                    </div>
                )}
                {summaryStatus === 'error' && summaryError && (
                    <div className="p-4 bg-red-900 border border-red-700 text-red-200 rounded-lg flex items-start gap-3">
                        <AlertTriangle size={20} className="text-red-400 mt-0.5 flex-shrink-0" />
                        <div>
                            <h3 className="font-semibold">Summary Error:</h3>
                            <p className="text-sm">{summaryError}</p>
                            <button
                                onClick={fetchDailySummary}
                                className="mt-2 text-xs px-2 py-1 bg-red-700 hover:bg-red-600 rounded"
                            >
                                Try Again
                            </button>
                        </div>
                    </div>
                )}
                {summaryStatus === 'success' && summary && (
                    <div className="prose prose-sm prose-invert max-w-none text-zinc-300">
                        <ReactMarkdown
                            components={{
                                p: ({ children }) => <p className="mb-2">{children}</p>,
                                ul: ({ children }) => <ul className="list-disc pl-5 mb-2">{children}</ul>,
                                ol: ({ children }) => <ol className="list-decimal pl-5 mb-2">{children}</ol>,
                                li: ({ children }) => <li className="mb-1">{children}</li>,
                                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                                h1: ({ children }) => <h1 className="text-xl font-bold mt-4 mb-2">{children}</h1>,
                                h2: ({ children }) => <h2 className="text-lg font-semibold mt-3 mb-2">{children}</h2>,
                                h3: ({ children }) => <h3 className="text-base font-semibold mt-2 mb-1">{children}</h3>,
                            }}
                        >
                            {summary}
                        </ReactMarkdown>
                    </div>
                )}
                {summaryStatus === 'success' && !summary && (
                    <p className="text-zinc-400 flex items-center gap-2">
                        <Info size={16} />
                        No summary available for today, or no emails found.
                    </p>
                )}
                {summaryGeneratedAt && summaryStatus === 'success' && (
                    <p className="text-xs text-zinc-500 mt-4">
                        Summary generated at: {new Date(summaryGeneratedAt).toLocaleString()}
                    </p>
                )}
            </section>
        </div>
    );
}