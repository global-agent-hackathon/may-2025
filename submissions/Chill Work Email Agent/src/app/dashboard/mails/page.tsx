
'use client';

import { useState, useEffect, useCallback } from 'react';
import MailList from '@/components/sections/MailList';
import ViewMail from '@/components/sections/ViewMail';
import { ArrowLeft, AlertTriangle } from 'lucide-react';
import type { MailReadClient } from '@/types/mail';
import { MailTagClientValue } from '@/types/mail';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const MAILS_PER_PAGE = 20;

interface CategoryState {
    current: MailTagClientValue;
    all: MailTagClientValue[];
    changeCategory: (category: MailTagClientValue) => void;
}

interface MailListProps {
    mails: MailReadClient[];
    selectedMailId: number | null; // Updated to match MailReadClient.id type
    onSelectMail: (mail: MailReadClient) => void;
    onLoadMore: () => void;
    hasMore: boolean;
    isLoadingMore: boolean;
    categoryState: CategoryState;
}

export default function InboxPage() {
    const [selectedMail, setSelectedMail] = useState<MailReadClient | null>(null);
    const [mails, setMails] = useState<MailReadClient[]>([]);
    const [currentCategory, setCurrentCategory] = useState<MailTagClientValue>(MailTagClientValue.INBOX);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [skip, setSkip] = useState<number>(0);
    const [hasMore, setHasMore] = useState<boolean>(true);

    const fetchMails = useCallback(
        async (category: MailTagClientValue, currentSkip: number, loadMore: boolean = false) => {
            if (!loadMore) {
                setIsLoading(true);
                setMails([]);
                setSelectedMail(null);
            } else {
                setIsLoadingMore(true);
            }
            setError(null);

            try {
                const response = await fetch(
                    `${API_BASE_URL}/api/mails/${category}?skip=${currentSkip}&limit=${MAILS_PER_PAGE}`,
                    { credentials: 'include' }
                );
                if (response.status === 401) {
                    throw new Error('Unauthorized. Please login again.');
                }
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Error fetching mails: ${response.statusText}`);
                }
                const newMails: MailReadClient[] = await response.json();

                setMails((prevMails) => (loadMore ? [...prevMails, ...newMails] : newMails));
                setHasMore(newMails.length === MAILS_PER_PAGE);
                if (!loadMore && newMails.length > 0) {
                    setSelectedMail(newMails[0]);
                }
            } catch (err: any) {
                setError(err.message);
                console.error('Failed to fetch mails:', err);
            } finally {
                setIsLoading(false);
                setIsLoadingMore(false);
            }
        },
        []
    );

    useEffect(() => {
        setSkip(0);
        setHasMore(true);
        fetchMails(currentCategory, 0, false);
    }, [currentCategory, fetchMails]);

    const handleSelectMail = useCallback((mail: MailReadClient) => {
        setSelectedMail(mail);
    }, []);

    const handleBackToList = useCallback(() => {
        setSelectedMail(null);
    }, []);

    const handleLoadMore = useCallback(() => {
        if (hasMore && !isLoadingMore) {
            const nextSkip = skip + MAILS_PER_PAGE;
            setSkip(nextSkip);
            fetchMails(currentCategory, nextSkip, true);
        }
    }, [hasMore, isLoadingMore, skip, currentCategory, fetchMails]);

    const changeCategory = useCallback(
        (newCategory: MailTagClientValue) => {
            if (newCategory !== currentCategory) {
                setCurrentCategory(newCategory);
            }
        },
        [currentCategory]
    );

    const categoryState: CategoryState = {
        current: currentCategory,
        all: Object.values(MailTagClientValue) as MailTagClientValue[],
        changeCategory,
    };

    if (isLoading && mails.length === 0 && !isLoadingMore) {
        return (
            <div className="flex items-center justify-center h-[calc(100vh-4rem)] text-zinc-100">
                Loading mails...
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-[calc(100vh-4rem)] text-red-500 p-4">
                <div className="flex items-center gap-2 bg-zinc-700 rounded-lg p-3">
                    <AlertTriangle size={18} />
                    <span>Error: {error}</span>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-[calc(100vh-4rem)] bg-zinc-900 rounded-lg shadow-md overflow-hidden">
            <div
                className={`w-full md:w-80 lg:w-96 bg-zinc-900 border-r border-zinc-700 transition-transform duration-300 ease-in-out flex flex-col ${selectedMail ? 'hidden md:flex' : 'flex'
                    }`}
            >
                <MailList
                    mails={mails}
                    selectedMailId={selectedMail?.id ?? null}
                    onSelectMail={handleSelectMail}
                    onLoadMore={handleLoadMore}
                    hasMore={hasMore}
                    isLoadingMore={isLoadingMore}
                    categoryState={categoryState}
                />
            </div>
            <div className="flex-1 p-0 md:p-4 relative bg-zinc-900">
                {selectedMail ? (
                    <>
                        <button
                            className="md:hidden absolute top-4 left-4 text-zinc-100 p-2 rounded-full bg-zinc-700 hover:bg-zinc-500 z-20"
                            onClick={handleBackToList}
                            aria-label="Back to mail list"
                        >
                            <ArrowLeft size={18} />
                        </button>
                        <ViewMail mail={selectedMail} />
                    </>
                ) : (
                    <div className="hidden md:flex items-center justify-center h-full text-zinc-500 text-base">
                        Select an email to view
                    </div>
                )}
            </div>
        </div>
    );
}