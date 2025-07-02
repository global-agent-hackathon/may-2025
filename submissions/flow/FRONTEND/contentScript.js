// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'injectFont') {
        try {
            // First inject the font
            const link = document.createElement('link');
            link.href = request.fontUrl;
            link.rel = 'stylesheet';
            document.head.appendChild(link);

            // Then apply the font
            const style = document.createElement('style');
            style.textContent = request.css;
            document.head.appendChild(style);

            sendResponse({ success: true });
        } catch (error) {
            console.error('Error injecting font:', error);
            sendResponse({ success: false, error: error.message });
        }
        return true; // Keep the message channel open for the async response
    }
}); 