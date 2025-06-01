// AI Chatbot Content Script
let chatWindow = null;
let isDragging = false;
let dragOffset = { x: 0, y: 0 };
let messagesContainer = null;

// Global addMessage function
function addMessage(role, content) {
    if (!messagesContainer) {
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.style.maxWidth = '85%';
    messageDiv.style.padding = '12px 16px';
    messageDiv.style.borderRadius = '12px';
    messageDiv.style.fontSize = '14px';
    messageDiv.style.lineHeight = '1.5';
    messageDiv.style.whiteSpace = 'pre-wrap';
    messageDiv.style.wordBreak = 'break-word';
    messageDiv.style.boxShadow = '0 1px 2px rgba(0,0,0,0.05)';

    if (role === 'user') {
        messageDiv.style.alignSelf = 'flex-end';
        messageDiv.style.backgroundColor = '#0a5ecb';
        messageDiv.style.color = '#fff';
    } else {
        messageDiv.style.alignSelf = 'flex-start';
        messageDiv.style.backgroundColor = '#ffffff';
        messageDiv.style.color = '#1a1a1a';
        messageDiv.style.border = '1px solid #f0f0f0';
    }

    // Process markdown formatting
    const formattedContent = content
    // Handle headers
        .replace(/^### (.*$)/gm, '<h3 style="font-size: 16px; font-weight: 600; margin: 16px 0 8px 0; color: #1a1a1a;">$1</h3>')
        .replace(/^## (.*$)/gm, '<h2 style="font-size: 18px; font-weight: 600; margin: 20px 0 12px 0; color: #1a1a1a;">$1</h2>')
        .replace(/^# (.*$)/gm, '<h1 style="font-size: 20px; font-weight: 600; margin: 24px 0 16px 0; color: #1a1a1a;">$1</h1>')

    // Handle bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600;">$1</strong>')

    // Handle italic text
        .replace(/\*(.*?)\*/g, '<em style="font-style: italic;">$1</em>')

    // Handle lists
        .replace(/^\d+\. (.*$)/gm, '<div style="margin: 4px 0; padding-left: 20px;">$1</div>')
        .replace(/^• (.*$)/gm, '<div style="margin: 4px 0; padding-left: 20px;">• $1</div>')

    // Handle paragraphs
        .replace(/\n\n/g, '<br><br>')

    // Handle links
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" style="color: #0a5ecb; text-decoration: none; border-bottom: 1px solid #0a5ecb;">$1</a>');

    messageDiv.innerHTML = formattedContent;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function createChatWindow() {
    if (chatWindow) {
        return;
    }

    // Create main container
    chatWindow = document.createElement('div');
    chatWindow.style.position = 'fixed';
    chatWindow.style.bottom = '20px';
    chatWindow.style.right = '20px';
    chatWindow.style.width = '380px';
    chatWindow.style.height = '600px';
    chatWindow.style.backgroundColor = '#ffffff';
    chatWindow.style.borderRadius = '16px';
    chatWindow.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
    chatWindow.style.display = 'flex';
    chatWindow.style.flexDirection = 'column';
    chatWindow.style.zIndex = '2147483647';
    chatWindow.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    chatWindow.style.overflow = 'hidden';
    chatWindow.style.transition = 'all 0.3s ease';

    // Create header
    const header = document.createElement('div');
    header.style.padding = '16px 20px';
    header.style.backgroundColor = '#ffffff';
    header.style.borderBottom = '1px solid #f0f0f0';
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';
    header.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 2px;">
      <span style="font-size: 16px; font-weight: 600; color: #1a1a1a; display: flex; align-items: center; gap: 6px;">
        <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m10.051 8.102-3.778.322-1.994 1.994a.94.94 0 0 0 .533 1.6l2.698.316m8.39 1.617-.322 3.78-1.994 1.994a.94.94 0 0 1-1.595-.533l-.4-2.652m8.166-11.174a1.366 1.366 0 0 0-1.12-1.12c-1.616-.279-4.906-.623-6.38.853-1.671 1.672-5.211 8.015-6.31 10.023a.932.932 0 0 0 .162 1.111l.828.835.833.832a.932.932 0 0 0 1.111.163c2.008-1.102 8.35-4.642 10.021-6.312 1.475-1.478 1.133-4.77.855-6.385Zm-2.961 3.722a1.88 1.88 0 1 1-3.76 0 1.88 1.88 0 0 1 3.76 0Z"/>
</svg>

        Flowy
      </span>
      <span style="font-size: 10px; color: #888; font-weight: 400;">Powered by Browser-use</span>
    </div>
    <div style="display: flex; gap: 8px; align-items: center;">
      <button id="voice-toggle" style="background: none; border: none; color: #666; cursor: pointer; font-size: 16px; padding: 6px; border-radius: 6px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
          <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
        </svg>
      </button>
      <button id="close-chat" style="background: none; border: none; color: #666; cursor: pointer; font-size: 20px; padding: 4px; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease;">×</button>
    </div>
  `;
    chatWindow.appendChild(header);

    // Create chat messages container
    messagesContainer = document.createElement('div');
    messagesContainer.style.flex = '1';
    messagesContainer.style.overflowY = 'auto';
    messagesContainer.style.padding = '20px';
    messagesContainer.style.display = 'flex';
    messagesContainer.style.flexDirection = 'column';
    messagesContainer.style.gap = '16px';
    messagesContainer.style.backgroundColor = '#fafafa';
    chatWindow.appendChild(messagesContainer);

    // Create input container
    const inputContainer = document.createElement('div');
    inputContainer.style.padding = '16px 20px';
    inputContainer.style.backgroundColor = '#ffffff';
    inputContainer.style.borderTop = '1px solid #f0f0f0';
    inputContainer.style.display = 'flex';
    inputContainer.style.flexDirection = 'column';
    inputContainer.style.gap = '12px';

    // Create summarize button
    const summarizeButton = document.createElement('button');
    summarizeButton.textContent = 'Summarize Page';
    summarizeButton.style.padding = '10px 16px';
    summarizeButton.style.backgroundColor = '#f5f5f5';
    summarizeButton.style.color = '#1a1a1a';
    summarizeButton.style.border = 'none';
    summarizeButton.style.borderRadius = '8px';
    summarizeButton.style.cursor = 'pointer';
    summarizeButton.style.fontSize = '14px';
    summarizeButton.style.fontWeight = '500';
    summarizeButton.style.transition = 'all 0.2s ease';
    summarizeButton.style.display = 'flex';
    summarizeButton.style.alignItems = 'center';
    summarizeButton.style.justifyContent = 'center';
    summarizeButton.style.gap = '8px';
    summarizeButton.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="16" y1="13" x2="8" y2="13"></line>
      <line x1="16" y1="17" x2="8" y2="17"></line>
      <polyline points="10 9 9 9 8 9"></polyline>
    </svg>
    Summarize Page
  `;
    summarizeButton.addEventListener('mouseover', () => {
        summarizeButton.style.backgroundColor = '#eaeaea';
    });
    summarizeButton.addEventListener('mouseout', () => {
        summarizeButton.style.backgroundColor = '#f5f5f5';
    });
    summarizeButton.addEventListener('click', summarizePage);
    inputContainer.appendChild(summarizeButton);

    // Create input field container
    const inputFieldContainer = document.createElement('div');
    inputFieldContainer.style.display = 'flex';
    inputFieldContainer.style.gap = '8px';
    inputFieldContainer.style.backgroundColor = '#f5f5f5';
    inputFieldContainer.style.borderRadius = '12px';
    inputFieldContainer.style.padding = '4px';
    inputContainer.appendChild(inputFieldContainer);

    // Create microphone button
    const micButton = document.createElement('button');
    micButton.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>
  `;
    micButton.style.padding = '8px';
    micButton.style.backgroundColor = '#f5f5f5';
    micButton.style.color = '#666';
    micButton.style.border = 'none';
    micButton.style.borderRadius = '8px';
    micButton.style.cursor = 'pointer';
    micButton.style.display = 'flex';
    micButton.style.alignItems = 'center';
    micButton.style.justifyContent = 'center';
    micButton.style.transition = 'all 0.2s ease';
    inputFieldContainer.appendChild(micButton);

    // Create input field
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Ask me anything about this page...';
    input.style.flex = '1';
    input.style.padding = '12px 16px';
    input.style.border = 'none';
    input.style.borderRadius = '8px';
    input.style.fontSize = '14px';
    input.style.backgroundColor = 'transparent';
    input.style.outline = 'none';
    inputFieldContainer.appendChild(input);

    // Create send button
    const sendButton = document.createElement('button');
    sendButton.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="22" y1="2" x2="11" y2="13"></line>
      <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
    </svg>
  `;
    sendButton.style.padding = '8px';
    sendButton.style.backgroundColor = '#0a5ecb';
    sendButton.style.color = '#fff';
    sendButton.style.border = 'none';
    sendButton.style.borderRadius = '8px';
    sendButton.style.cursor = 'pointer';
    sendButton.style.display = 'flex';
    sendButton.style.alignItems = 'center';
    sendButton.style.justifyContent = 'center';
    sendButton.style.transition = 'all 0.2s ease';
    inputFieldContainer.appendChild(sendButton);

    chatWindow.appendChild(inputContainer);
    document.body.appendChild(chatWindow);

    // Add welcome message
    addMessage('assistant', 'Hello! I\'m your Flowy. I can help you with:\n• Answering questions about this tab\n • Helping with Mails\n• Filling forms\n• Extracting data\n\nWhat would you like help with?');

    // Add event listeners
    header.addEventListener('mousedown', startDragging);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDragging);

    document.getElementById('close-chat').addEventListener('click', () => {
        chatWindow.remove();
        chatWindow = null;
    });

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    sendButton.addEventListener('click', sendMessage);
    sendButton.addEventListener('mouseover', () => {
        sendButton.style.backgroundColor = '#094db3';
    });
    sendButton.addEventListener('mouseout', () => {
        sendButton.style.backgroundColor = '#0a5ecb';
    });

    // Add voice recognition functionality
    let recognition = null;
    let isListening = false;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            sendMessage();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            addMessage('assistant', 'Sorry, there was an error with voice recognition. Please try typing instead.');
        };

        recognition.onend = () => {
            isListening = false;
            micButton.style.backgroundColor = '#f5f5f5';
            micButton.style.color = '#666';
        };
    }

    micButton.addEventListener('click', () => {
        if (!recognition) {
            addMessage('assistant', 'Voice recognition is not supported in your browser. Please use typing instead.');
            return;
        }

        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
            isListening = true;
            micButton.style.backgroundColor = '#0a5ecb';
            micButton.style.color = '#fff';
        }
    });

    // Add voice toggle functionality
    let isVoiceEnabled = true;
    const voiceToggleButton = document.getElementById('voice-toggle');

    // Function to update voice button state
    function updateVoiceButtonState() {
        voiceToggleButton.style.color = isVoiceEnabled ? '#0a5ecb' : '#666';
        voiceToggleButton.innerHTML = isVoiceEnabled ?
            `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
        <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
      </svg>` :
            `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
        <line x1="23" y1="9" x2="17" y2="15"></line>
        <line x1="17" y1="9" x2="23" y2="15"></line>
      </svg>`;
    }

    // Initialize button state
    updateVoiceButtonState();

    voiceToggleButton.addEventListener('click', () => {
        isVoiceEnabled = !isVoiceEnabled;
        updateVoiceButtonState();

        if (!isVoiceEnabled) {
            // Stop any ongoing speech
            window.speechSynthesis.cancel();
            // Clear any queued utterances
            window.speechSynthesis.resume();
            window.speechSynthesis.pause();
        }
    });

    // Modify the speakText function to respect the voice toggle
    function speakText(text) {
        if (!isVoiceEnabled) {
            return;
        }

        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech before starting new one
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';

            // Add error handling
            utterance.onerror = (event) => {
                console.error('Speech synthesis error:', event);
            };

            // Add end event to clean up
            utterance.onend = () => {
                if (!isVoiceEnabled) {
                    window.speechSynthesis.cancel();
                }
            };

            window.speechSynthesis.speak(utterance);
        }
    }

    // Modify the addMessage function to include text-to-speech
    const originalAddMessage = addMessage;
    addMessage = function (role, content) {
        originalAddMessage(role, content);
        if (role === 'assistant' && isVoiceEnabled) {
            speakText(content);
        }
    };

    // Make the chat window draggable
    function startDragging(e) {
        if (e.target.id === 'close-chat') {
            return;
        }
        isDragging = true;
        const rect = chatWindow.getBoundingClientRect();
        dragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    function drag(e) {
        if (!isDragging) {
            return;
        }
        e.preventDefault();
        chatWindow.style.left = (e.clientX - dragOffset.x) + 'px';
        chatWindow.style.top = (e.clientY - dragOffset.y) + 'px';
        chatWindow.style.right = 'auto';
        chatWindow.style.bottom = 'auto';
    }

    function stopDragging() {
        isDragging = false;
    }

    function sendMessage() {
        const message = input.value.trim();
        if (!message) {
            return;
        }

        addMessage('user', message);
        input.value = '';

        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.style.alignSelf = 'flex-start';
        typingDiv.style.padding = '10px 14px';
        typingDiv.style.backgroundColor = '#f0f2f5';
        typingDiv.style.borderRadius = '12px';
        typingDiv.style.fontSize = '14px';
        typingDiv.style.color = '#666';
        typingDiv.textContent = 'Let Flowy Cook...';
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Send message to backend
        fetch('http://localhost:5000/api/analyze-tab', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: message
                // Removed pageContent as requested
            })
        })
            .then(res => res.json())
            .then(data => {
                // Remove typing indicator
                typingDiv.remove();

                console.log('AI Chatbot backend response:', data); // Log the full response

                if (data.error) {
                    addMessage('assistant', 'Sorry, I encountered an error: ' + data.error);
                } else if (data.status === 'success') {
                    try {
                        // Attempt to display the analysis or message
                        addMessage('assistant', data.analysis || data.message || 'Analysis successful, but no details provided.'); // Use data.analysis or data.message
                    } catch (displayError) {
                        console.error('Error displaying assistant message:', displayError);
                        // Fallback to a simpler display or an error message if addMessage fails
                        addMessage('assistant', 'Sorry, I received the data, but failed to display it.');
                    }
                } else if (data.status === 'error') {
                    addMessage('assistant', 'Sorry, I encountered an error: ' + (data.message || 'An unknown error occurred on the backend.')); // Use data.message for backend errors
                } else {
                    addMessage('assistant', 'Received an unexpected response format from the backend.');
                }
            })
            .catch(error => {
                typingDiv.remove();
                addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
                console.error('Error:', error);
            });
    }
}

// Add summarizePage function
async function summarizePage() {
    const messagesContainer = chatWindow.querySelector('div[style*="flex: 1"]');

    // Show only one loading indicator
    const typingDiv = document.createElement('div');
    typingDiv.style.alignSelf = 'flex-start';
    typingDiv.style.padding = '10px 14px';
    typingDiv.style.backgroundColor = '#f0f2f5';
    typingDiv.style.borderRadius = '12px';
    typingDiv.style.fontSize = '14px';
    typingDiv.style.color = '#666';
    typingDiv.textContent = 'AI is analyzing the page...';  // Single loading message
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const response = await fetch('http://localhost:5000/api/analyze-tab', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: 'summarize the current page in 100 words'  // Updated to 100 words
            })
        });

        const data = await response.json();

        // Remove typing indicator
        typingDiv.remove();

        // Handle the response in a single block
        if (data.status === 'success') {
            addMessage('assistant', data.analysis || data.message || 'Summarization successful, but no details provided.');
        } else {
            addMessage('assistant', data.message || data.error || 'An error occurred during summarization.');
        }
    } catch (error) {
        // Remove typing indicator
        typingDiv.remove();
        addMessage('assistant', 'Sorry, I encountered an error while analyzing the page.');
    }
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    console.log('Content script received message:', msg);

    if (msg.action === 'ping') {
    // Respond to ping to confirm content script is loaded
        sendResponse({ status: 'pong' });
        return true;
    }

    if (msg.action === 'openAIChatbot') {
        try {
            createChatWindow();
            sendResponse({ status: 'opened' });
        } catch (error) {
            console.error('Error creating chat window:', error);
            sendResponse({ status: 'error', error: error.message });
        }
        return true;
    }

    return true;
});
