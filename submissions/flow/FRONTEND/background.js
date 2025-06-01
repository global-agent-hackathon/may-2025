// Keep track of popup state in chrome.storage
chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed - initializing...');
    // Initialize storage
    chrome.storage.local.set({ popupWindowId: null });

    // Create context menus
    chrome.contextMenus.create({
        id: 'pick-element',
        title: '🔍 Analyze Element',
        contexts: ['all']
    }, () => {
        if (chrome.runtime.lastError) {
            console.error('Error creating analyze menu:', chrome.runtime.lastError);
        } else {
            console.log('Analyze menu created successfully');
        }
    });

    // Create parent menu for translation
    chrome.contextMenus.create({
        id: 'translate-menu',
        title: '🌐 Translate To',
        contexts: ['all']
    }, () => {
        if (chrome.runtime.lastError) {
            console.error('Error creating translate menu:', chrome.runtime.lastError);
        } else {
            console.log('Translate menu created successfully');
        }
    });

    // Create AI Chatbot menu item
    chrome.contextMenus.create({
        id: 'ai-chatbot',
        title: '🤖 Flowy',
        contexts: ['all']
    }, () => {
        if (chrome.runtime.lastError) {
            console.error('Error creating AI chatbot menu:', chrome.runtime.lastError);
        } else {
            console.log('AI chatbot menu created successfully');
        }
    });

    // Create submenu items for each language with emojis
    const languages = [
        { id: 'translate-es', title: '🇪🇸 Spanish' },
        { id: 'translate-fr', title: '🇫🇷 French' },
        { id: 'translate-de', title: '🇩🇪 German' },
        { id: 'translate-ja', title: '🇯🇵 Japanese' },
        { id: 'translate-zh', title: '🇨🇳 Chinese' },
        { id: 'translate-ru', title: '🇷🇺 Russian' },
        { id: 'translate-ar', title: '🇸🇦 Arabic' },
        { id: 'translate-hi', title: '🇮🇳 Hindi' }
    ];

    languages.forEach(lang => {
        chrome.contextMenus.create({
            id: lang.id,
            parentId: 'translate-menu',
            title: lang.title,
            contexts: ['all']
        }, () => {
            if (chrome.runtime.lastError) {
                console.error(`Error creating ${lang.title} menu:`, chrome.runtime.lastError);
            } else {
                console.log(`${lang.title} menu created successfully`);
            }
        });
    });
});

// Listen for popup creation
chrome.action.onClicked.addListener(async () => {
    const { popupWindowId } = await chrome.storage.local.get('popupWindowId');

    if (!popupWindowId) {
        chrome.windows.create({
            url: 'popup.html',
            type: 'popup',
            width: 400,
            height: 600
        }, (window) => {
            chrome.storage.local.set({ popupWindowId: window.id });
        });
    } else {
    // If popup exists, focus it
        try {
            await chrome.windows.update(popupWindowId, { focused: true });
        } catch (error) {
            // If window doesn't exist anymore, create a new one
            chrome.windows.create({
                url: 'popup.html',
                type: 'popup',
                width: 400,
                height: 600
            }, (window) => {
                chrome.storage.local.set({ popupWindowId: window.id });
            });
        }
    }
});

// Listen for popup window close
chrome.windows.onRemoved.addListener(async (windowId) => {
    const { popupWindowId } = await chrome.storage.local.get('popupWindowId');
    if (windowId === popupWindowId) {
        chrome.storage.local.set({ popupWindowId: null });
    }
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    console.log('Context menu clicked:', info.menuItemId);
    console.log('Current tab:', tab);

    try {
        if (info.menuItemId === 'pick-element') {
            console.log('Sending analyze message to tab:', tab.id);
            await chrome.tabs.sendMessage(tab.id, { action: 'startElementPicker', mode: 'analyze' });
            console.log('Analyze message sent successfully');
        } else if (info.menuItemId.startsWith('translate-')) {
            const language = info.menuItemId.split('-')[1];
            console.log('Sending translate message to tab:', tab.id, 'for language:', language);
            await chrome.tabs.sendMessage(tab.id, {
                action: 'startElementPicker',
                mode: 'translate',
                language: language
            });
            console.log('Translate message sent successfully');
        } else if (info.menuItemId === 'ai-chatbot') {
            console.log('Sending AI chatbot message to tab:', tab.id);
            try {
                await chrome.tabs.sendMessage(tab.id, { action: 'ping' });
            } catch (error) {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['aiChatbot.js']
                });
            }
            await chrome.tabs.sendMessage(tab.id, { action: 'openAIChatbot' });
            console.log('AI chatbot message sent successfully');
        }
    } catch (error) {
        console.error('Error in context menu handler:', error);
        if (error.message.includes('Could not establish connection')) {
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['aiChatbot.js']
                });
                await chrome.tabs.sendMessage(tab.id, { action: 'openAIChatbot' });
                console.log('Message sent successfully after script injection');
            } catch (injectError) {
                console.error('Error injecting script:', injectError);
            }
        }
    }
});

// Listen for messages from the popup script
chrome.runtime.onMessage.addListener(async (request, sender, sendResponse) => {
    console.log('Message from popup:', request);

    // IMPORTANT: Return true immediately to indicate asynchronous response ONLY IF you will call sendResponse.
    // For actions that do not send an async response, return false or undefined.

    if (request.action === 'startElementPicker') {
        // ... existing code ...
        return false; // Explicitly return false as this doesn't use sendResponse asynchronously
    } else if (request.action === 'openAIChatbot') {
        // ... existing code ...
        return true; // Keep this true as openAIChatbot response is async
    }

    // For other messages, indicate that no asynchronous response will be sent
    return false;
});
