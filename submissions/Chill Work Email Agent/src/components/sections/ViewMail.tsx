'use client';

import type { MailReadClient } from '@/types/mail';
import { formatMailDateTime } from '@/utils/dateFormatter';
import DOMPurify from 'dompurify'; // for XSS attack of html content

interface ViewMailProps {
    mail: MailReadClient;
}

export default function ViewMail({ mail }: ViewMailProps) {
    const fromDisplay = mail.from_name || mail.from_address;
    const toDisplay = mail.to_name || mail.to_address;
    const subjectDisplay = mail.subject || "(no subject)";
    const dateDisplay = formatMailDateTime(mail.message_timestamp);
    const contentToDisplay = mail.content_plain || mail.content_html || "No content available.";
    const isHtmlContent = !!mail.content_html && !mail.content_plain;
    const sanitizedHtml = DOMPurify.sanitize(mail.content_html!);

    return (
        <div className="bg-zinc-900 p-4 md:p-6 rounded-lg shadow-md h-full flex flex-col">
            <div className="border-b border-zinc-700 pb-4 mb-4">
                <h2 className="text-lg font-medium text-zinc-100" title={subjectDisplay}>
                    {subjectDisplay}
                </h2>
                <div className="text-sm text-zinc-500 mt-2 space-y-1">
                    <p>
                        <span className="font-medium">From:</span> {fromDisplay}
                    </p>
                    <p>
                        <span className="font-medium">To:</span> {toDisplay}
                    </p>
                    <p>
                        <span className="font-medium">Date:</span> {dateDisplay}
                    </p>
                    {mail.tags && mail.tags.length > 0 && (
                        <p>
                            <span className="font-medium">Tags:</span> {mail.tags.join(', ')}
                        </p>
                    )}
                </div>
            </div>
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-500 scrollbar-track-zinc-900 text-zinc-100 text-sm leading-relaxed">
                {isHtmlContent ? (
                    <div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />
                ) : (
                    <pre className="whitespace-pre-wrap break-words font-sans">{contentToDisplay}</pre>
                )}
            </div>
            <div className="mt-4 pt-4 border-t border-zinc-700 flex gap-3">
                <button
                    className="bg-zinc-500 text-zinc-100 px-4 py-2 rounded-lg hover:bg-zinc-700 transition-colors duration-150"
                    aria-label="Reply to email"
                >
                    Reply
                </button>
            </div>
        </div>
    );
}