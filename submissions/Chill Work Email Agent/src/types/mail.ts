export enum MailTagClientValue {
    INBOX = "Inbox",
    IMPORTANT = "Important",
    ARCHIVE = "Archive",
    SENT = "Sent",
}

export interface MailReadClient {
    id: number;
    user_id: number;
    gmail_message_id: string;
    from_address: string;
    from_name?: string | null;
    to_address: string;
    to_name: string;
    message_timestamp: string;
    subject?: string | null;
    snippet?: string | null;
    content_html?: string | null;
    content_plain?: string | null;
    tags: string[];
    created_at: string;
    updated_at: string;
}