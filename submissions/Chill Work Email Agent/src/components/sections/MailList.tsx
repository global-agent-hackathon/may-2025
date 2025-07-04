'use client';

import type { MailReadClient } from '@/types/mail';
import { formatMailTimestamp } from '@/utils/dateFormatter';
import { MailTagClientValue } from '@/types/mail';

interface CategoryState {
    current: MailTagClientValue;
    all: MailTagClientValue[];
    changeCategory: (category: MailTagClientValue) => void;
}

interface MailListProps {
    mails: MailReadClient[];
    selectedMailId: number | null;
    onSelectMail: (mail: MailReadClient) => void;
    onLoadMore: () => void;
    hasMore: boolean;
    isLoadingMore: boolean;
    categoryState: CategoryState;
}

export default function MailList({
    mails,
    selectedMailId,
    onSelectMail,
    onLoadMore,
    hasMore,
    isLoadingMore,
    categoryState,
}: MailListProps) {
    const { current: currentCategory, all: categories, changeCategory } = categoryState;

    return (
        <div className="flex flex-col h-full text-zinc-100">
            <div className="p-4 border-b border-zinc-700">
                <h2 className="text-lg font-medium text-zinc-100 mb-3">{currentCategory}</h2>
                <div className="flex flex-wrap gap-2">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => changeCategory(cat)}
                            className={`px-3 py-1 text-sm rounded-lg transition-colors ${currentCategory === cat
                                ? 'bg-zinc-500 text-zinc-100'
                                : 'bg-zinc-700 text-zinc-100 hover:bg-zinc-500'
                                }`}
                            aria-label={`Switch to ${cat} category`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>
            </div>
            <ul className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-500 scrollbar-track-zinc-900">
                {mails.map((mail) => {
                    const fromDisplay = mail.from_name || mail.from_address;
                    const subjectDisplay = mail.subject || '(no subject)';
                    const dateDisplay = formatMailTimestamp(mail.message_timestamp);

                    return (
                        <li
                            key={mail.id}
                            className={`p-3 border-b border-zinc-700 hover:bg-zinc-700 cursor-pointer transition-colors duration-150 ${selectedMailId === mail.id ? 'bg-zinc-700' : ''
                                }`}
                            onClick={() => onSelectMail(mail)}
                            aria-label={`Select email from ${fromDisplay}`}
                        >
                            <div className="flex justify-between items-start gap-2">
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium truncate" title={fromDisplay}>
                                        {fromDisplay}
                                    </p>
                                    <p className="text-sm font-medium mt-1 truncate" title={subjectDisplay}>
                                        {subjectDisplay}
                                    </p>
                                    <p className="text-xs text-zinc-500 mt-1 line-clamp-2">
                                        {mail.snippet || ''}
                                    </p>
                                </div>
                                <span className="text-xs text-zinc-500 flex-shrink-0">{dateDisplay}</span>
                            </div>
                        </li>
                    );
                })}
                {hasMore && (
                    <li className="p-3 text-center">
                        <button
                            onClick={onLoadMore}
                            disabled={isLoadingMore}
                            className="text-sm text-zinc-500 hover:text-zinc-100 disabled:text-zinc-600"
                            aria-label="Load more emails"
                        >
                            {isLoadingMore ? 'Loading...' : 'Load More'}
                        </button>
                    </li>
                )}
                {!hasMore && mails.length > 0 && (
                    <li className="p-3 text-center text-xs text-zinc-500">
                        No more messages.
                    </li>
                )}
                {mails.length === 0 && !isLoadingMore && (
                    <li className="p-3 text-center text-zinc-500 text-sm">
                        No messages in {currentCategory}.
                    </li>
                )}
            </ul>
        </div>
    );
}