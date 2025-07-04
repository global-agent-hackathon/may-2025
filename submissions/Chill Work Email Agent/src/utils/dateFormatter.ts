export function formatMailTimestamp(isoString: string): string {
    if (!isoString) return "Unknown Date";
    try {
        const date = new Date(isoString);
        return date.toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    } catch (e) {
        console.error("Error formatting date:", isoString, e);
        return "Invalid Date";
    }
}

export function formatMailDateTime(isoString: string): string {
    if (!isoString) return "Unknown Date";
    try {
        const date = new Date(isoString);
        return date.toLocaleString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    } catch (e) {
        console.error("Error formatting date:", isoString, e);
        return "Invalid Date";
    }
}