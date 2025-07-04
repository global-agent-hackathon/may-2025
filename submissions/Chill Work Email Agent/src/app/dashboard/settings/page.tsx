'use client';

import { useState, useEffect, FormEvent } from 'react';
import { LogOut, Save, Loader2, AlertTriangle, CheckCircle } from 'lucide-react'; // Added icons
import { redirect } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UserSettings {
    category_instruction: string | null;
    // Add other user details if needed from the /api/users/me endpoint
    email?: string;
    name?: string;
}

export default function SettingsPage() {
    const [categoryInstruction, setCategoryInstruction] = useState('');
    const [initialInstruction, setInitialInstruction] = useState(''); // To track changes

    const [isLoading, setIsLoading] = useState(false); // For fetching initial data
    const [isSaving, setIsSaving] = useState(false); // For saving data

    const [fetchError, setFetchError] = useState<string | null>(null);
    const [saveError, setSaveError] = useState<string | null>(null);
    const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

    // Fetch current user settings on component mount
    useEffect(() => {
        const fetchUserSettings = async () => {
            setIsLoading(true);
            setFetchError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/api/users/me`, {
                    credentials: 'include',
                });
                if (!response.ok) {
                    const errData = await response.json().catch(() => null);
                    throw new Error(errData?.detail || `Failed to fetch user settings: ${response.statusText}`);
                }
                const data: UserSettings = await response.json();
                setCategoryInstruction(data.category_instruction || '');
                setInitialInstruction(data.category_instruction || '');
            } catch (error: any) {
                setFetchError(error.message);
                console.error("Fetch user settings error:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchUserSettings();
    }, []);

    const handleSaveSettings = async (e: FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setSaveError(null);
        setSaveSuccess(null);

        try {
            const response = await fetch(`${API_BASE_URL}/api/users/me/settings/category-instruction`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ category_instruction: categoryInstruction }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to save settings.');
            }
            setSaveSuccess('Categorization rules saved successfully!');
            setInitialInstruction(categoryInstruction); // Update initial state after successful save
            setTimeout(() => setSaveSuccess(null), 3000); // Clear success message after 3s
        } catch (error: any) {
            setSaveError(error.message);
            console.error("Save settings error:", error);
        } finally {
            setIsSaving(false);
        }
    };

    // Basic logout - in a real app, this would call a backend /logout endpoint
    // and then redirect or clear local auth state.
    const handleLogout = async () => {
        console.log('Logout clicked');
        try {
            const response = await fetch(`${API_BASE_URL}/logout`, { method: 'POST', credentials: 'include' });
            redirect('/');
        } catch (err: any) {
            console.error("Error fetching user data:", err);
        }

        // Then redirect: window.location.href = '/login';
        alert("Logout functionality not fully implemented in this example.");
    };

    const hasChanges = categoryInstruction !== initialInstruction;

    if (isLoading) {
        return (
            <div className="min-h-screen bg-zinc-950 text-white p-6 flex items-center justify-center">
                <Loader2 size={32} className="animate-spin text-blue-500" />
                <p className="ml-3 text-lg">Loading settings...</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-900 text-zinc-100 p-4 md:p-6">
            <header className="pb-4 mb-6 border-b border-zinc-700">
                <h1 className="text-2xl font-semibold text-white">Settings</h1>
            </header>

            {fetchError && (
                <div className="mb-6 p-4 bg-zinc-700 border border-zinc-500 text-zinc-100 rounded-lg flex items-start gap-3">
                    <AlertTriangle size={18} className="text-zinc-500 mt-0.5 flex-shrink-0" />
                    <div>
                        <h3 className="font-medium text-zinc-100">Error Loading Settings:</h3>
                        <p className="text-sm text-zinc-100">{fetchError}</p>
                    </div>
                </div>
            )}

            <main className="space-y-8 max-w-2xl mx-auto">
                <form onSubmit={handleSaveSettings} className="space-y-6 p-4 bg-zinc-900 rounded-lg shadow-md border border-zinc-700">
                    <div>
                        <label className="block text-base font-medium text-zinc-100 mb-1" htmlFor="category-rules">
                            Email Categorization Instructions
                        </label>
                        <p className="text-sm text-zinc-500 mb-3">
                            Provide instructions for the AI to categorize your emails (e.g., into 'Important' or 'Archive').
                            Be specific about keywords, senders, or topics.
                        </p>
                        <textarea
                            id="category-rules"
                            placeholder="Example: Mark emails from 'boss@example.com' or containing 'urgent project update' as Important. Archive all newsletters."
                            rows={6}
                            className="w-full p-3 bg-zinc-700 text-zinc-100 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-zinc-500 focus:border-zinc-500 outline-none resize-y text-sm leading-relaxed scrollbar-thin scrollbar-thumb-zinc-500 scrollbar-track-zinc-900"
                            value={categoryInstruction}
                            onChange={(e) => setCategoryInstruction(e.target.value)}
                            disabled={isSaving}
                            aria-label="Email categorization instructions"
                        />
                    </div>

                    <div className="flex flex-col sm:flex-row items-center gap-3">
                        <button
                            type="submit"
                            disabled={isSaving || !hasChanges}
                            className="w-full sm:w-auto flex items-center justify-center gap-2 bg-zinc-500 text-zinc-100 font-medium py-2 px-5 rounded-lg hover:bg-zinc-700 focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2 focus:ring-offset-zinc-900 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isSaving ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                            {isSaving ? 'Saving...' : 'Save Instructions'}
                        </button>
                        {saveError && (
                            <div className="text-sm text-red-500 flex items-center gap-1.5">
                                <AlertTriangle size={14} /> {saveError}
                            </div>
                        )}
                        {saveSuccess && (
                            <div className="text-sm text-green-500 flex items-center gap-1.5">
                                <CheckCircle size={14} /> {saveSuccess}
                            </div>
                        )}
                    </div>
                </form>

                <div className="p-4 bg-zinc-900 rounded-lg shadow-md border border-zinc-700">
                    <h2 className="text-base font-medium text-zinc-100 mb-3">Account</h2>
                    <button
                        className="flex items-center gap-2 bg-zinc-500 text-zinc-100 font-medium py-2 px-4 rounded-lg hover:bg-zinc-700 focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2 focus:ring-offset-zinc-900 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={handleLogout}
                        disabled={isSaving}
                    >
                        <LogOut size={18} />
                        Log Out
                    </button>
                </div>
            </main>
        </div>
    );
}