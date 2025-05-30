// VibeProto Frontend Script with "Think" Feature
// ----------------------------------------------
// This file replaces the previous implementation and adds:
// 1. "Think" option to generate reasoning behind code.
// 2. Simplified chat + code display interface.
// NOTE: Menu features (rename/delete) are removed per the new spec.

let currentSessionId = null;
let sessions = [];
let userId = "default_user"; // Hardcoded for now; can be made dynamic later
let remoteMode = false;
let activeRemoteTasks = {};
let taskStatusCheckInterval = null;
let codeEditor = null; // Global codeEditor variable
let lastGeneratedCode = null;

// Multimodal input tracking
let multimodalInputs = {
    image: null,
    audio: null,
    video: null
};

// Multimodal file handling functions
function handleFileSelection(fileInput, mediaType) {
    const file = fileInput.files[0];
    if (!file) {
        multimodalInputs[mediaType] = null;
        updateMultimodalPreview();
        return;
    }
    
    // Validate file size (max 100MB for videos)
    const maxSize = mediaType === 'video' ? 100 * 1024 * 1024 : 50 * 1024 * 1024;
    if (file.size > maxSize) {
        const maxSizeMB = mediaType === 'video' ? 100 : 50;
        showNotification(`File too large. Maximum size is ${maxSizeMB}MB for ${mediaType}.`, 'error');
        fileInput.value = '';
        return;
    }
    
    // Convert to base64
    const reader = new FileReader();
    reader.onload = function(e) {
        multimodalInputs[mediaType] = {
            base64: e.target.result.split(',')[1], // Remove data:type;base64, prefix
            name: file.name,
            type: file.type,
            size: file.size
        };
        updateMultimodalPreview();
    };
    reader.onerror = function() {
        showNotification(`Error reading ${mediaType} file`, 'error');
        fileInput.value = '';
    };
    reader.readAsDataURL(file);
}

function updateMultimodalPreview() {
    const previewContainer = document.getElementById('multimodal-preview');
    if (!previewContainer) return;
    
    previewContainer.innerHTML = '';
    
    // Show preview for each attached media
    Object.keys(multimodalInputs).forEach(mediaType => {
        const media = multimodalInputs[mediaType];
        if (media) {
            const previewItem = document.createElement('div');
            previewItem.className = 'media-preview-item';
            
            let previewContent = '';
            
            if (mediaType === 'image') {
                previewContent = `
                    <img src="data:${media.type};base64,${media.base64}" alt="${media.name}">
                    <div class="media-info">
                        <div class="media-name">${media.name}</div>
                        <div class="media-type">Image (${formatFileSize(media.size)})</div>
                    </div>
                `;
            } else if (mediaType === 'audio') {
                previewContent = `
                    <div style="width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; background: #3a3a3a; border-radius: 4px;">
                        🎵
                    </div>
                    <div class="media-info">
                        <div class="media-name">${media.name}</div>
                        <div class="media-type">Audio (${formatFileSize(media.size)})</div>
                    </div>
                `;
            } else if (mediaType === 'video') {
                previewContent = `
                    <div style="width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; background: #3a3a3a; border-radius: 4px;">
                        🎥
                    </div>
                    <div class="media-info">
                        <div class="media-name">${media.name}</div>
                        <div class="media-type">Video (${formatFileSize(media.size)})</div>
                    </div>
                `;
            }
            
            previewContent += `<button class="remove-media" onclick="removeMultimodalInput('${mediaType}')">Remove</button>`;
            
            previewItem.innerHTML = previewContent;
            previewContainer.appendChild(previewItem);
        }
    });
}

function removeMultimodalInput(mediaType) {
    multimodalInputs[mediaType] = null;
    
    // Clear the file input
    const fileInput = document.getElementById(`${mediaType}-upload`);
    if (fileInput) {
        fileInput.value = '';
    }
    
    updateMultimodalPreview();
}

// Make removeMultimodalInput globally available for onclick handlers
window.removeMultimodalInput = removeMultimodalInput;

// Speech Recognition functionality
let recognition = null;
let isRecording = false;

function initSpeechRecognition() {
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        // Hide mic button if not supported
        const micButton = document.getElementById('mic-button');
        if (micButton) {
            micButton.style.display = 'none';
        }
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    // Use browser language or default to English
    recognition.lang = navigator.language || 'en-US';
    
    let finalTranscript = '';
    
    recognition.onstart = function() {
        console.log('Speech recognition started');
        isRecording = true;
        const micButton = document.getElementById('mic-button');
        if (micButton) {
            micButton.classList.add('recording');
            micButton.innerHTML = '🔴 Recording...';
        }
        
        // Get existing text to append to
        const promptTextarea = document.getElementById('prompt');
        if (promptTextarea && promptTextarea.value) {
            finalTranscript = promptTextarea.value + ' ';
        }
    };
    
    recognition.onresult = function(event) {
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update the prompt textarea with the transcript
        const promptTextarea = document.getElementById('prompt');
        if (promptTextarea) {
            promptTextarea.value = finalTranscript + interimTranscript;
        }
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        isRecording = false;
        const micButton = document.getElementById('mic-button');
        if (micButton) {
            micButton.classList.remove('recording');
            micButton.innerHTML = '🎤 Mic';
        }
        
        if (event.error === 'no-speech') {
            showNotification('No speech detected. Please try again.', 'info');
        } else if (event.error === 'not-allowed') {
            showNotification('Microphone access denied. Please allow microphone access.', 'error');
        } else {
            showNotification(`Speech recognition error: ${event.error}`, 'error');
        }
    };
    
    recognition.onend = function() {
        console.log('Speech recognition ended');
        isRecording = false;
        const micButton = document.getElementById('mic-button');
        if (micButton) {
            micButton.classList.remove('recording');
            micButton.innerHTML = '🎤 Mic';
        }
        finalTranscript = '';
    };
}

function toggleSpeechRecognition() {
    if (!recognition) {
        showNotification('Speech recognition not supported in this browser', 'error');
        return;
    }
    
    if (isRecording) {
        recognition.stop();
    } else {
        try {
            recognition.start();
        } catch (e) {
            if (e.message.includes('already started')) {
                recognition.stop();
                setTimeout(() => {
                    recognition.start();
                }, 100);
            } else {
                console.error('Error starting speech recognition:', e);
                showNotification('Error starting speech recognition', 'error');
            }
        }
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function getActiveMultimodalInput() {
    // Return the first non-null multimodal input
    for (const [type, data] of Object.entries(multimodalInputs)) {
        if (data) {
            return { type, data };
        }
    }
    return null;
}

// Professional notification system
function createNotificationSystem() {
    // Create notification container if it doesn't exist
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            pointer-events: none;
        `;
        document.body.appendChild(notificationContainer);
    }
    return notificationContainer;
}

function showNotification(message, type = 'success', duration = 4000) {
    const container = createNotificationSystem();
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        background: ${type === 'success' ? 'linear-gradient(135deg, #10b981, #34d399)' : 
                    type === 'error' ? 'linear-gradient(135deg, #ef4444, #f87171)' : 
                    'linear-gradient(135deg, #3b82f6, #60a5fa)'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 12px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 500;
        font-size: 14px;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
        pointer-events: auto;
        cursor: pointer;
        position: relative;
    `;
    
    // Add icon based on type
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 16px;">${icon}</span>
            <span>${message}</span>
            <span style="margin-left: auto; opacity: 0.7; font-size: 12px;">×</span>
        </div>
    `;
    
    // Add animation styles
    if (!document.getElementById('notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    container.appendChild(notification);
    
    // Auto-remove notification
    const removeNotification = () => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    };
    
    // Click to dismiss
    notification.addEventListener('click', removeNotification);
    
    // Auto-dismiss after duration
    setTimeout(removeNotification, duration);
}

// Loading animation for code generation
function showLoadingInCodeArea() {
    const codeDisplayElement = document.getElementById('code-display');
    if (codeDisplayElement) {
        codeDisplayElement.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; color: #64748b;">
                <div class="spinner" style="
                    width: 48px;
                    height: 48px;
                    border: 4px solid #e2e8f0;
                    border-top: 4px solid #3b82f6;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 16px;
                "></div>
                <div style="font-size: 16px; font-weight: 500; margin-bottom: 8px;">Generating Code...</div>
                <div style="font-size: 14px; opacity: 0.7;">Creating your professional web application</div>
            </div>
        `;
        
        // Add spinner animation if not already added
        if (!document.getElementById('spinner-styles')) {
            const styles = document.createElement('style');
            styles.id = 'spinner-styles';
            styles.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            `;
            document.head.appendChild(styles);
        }
    }
}

// Window load handler - we'll no longer automatically load code from localStorage
window.onload = function() {
    console.log("Window loaded");
    // Don't automatically load code from localStorage on initial page load
};

// Initialize CodeMirror
function initCodeMirror() {
    const codeEditorElement = document.getElementById('code-editor');
    if (!codeEditorElement) {
        console.error('Code editor element not found');
        return;
    }
    
    // Check if CodeMirror is already initialized on this element
    if (codeEditor && codeEditor.getWrapperElement() && codeEditor.getWrapperElement().parentNode === codeEditorElement) {
        console.log("CodeMirror already initialized, refreshing");
        codeEditor.refresh();
        return codeEditor;
    }
    
    try {
        // Clean the container if it already has content
        codeEditorElement.innerHTML = '';
        
        // Simple initialization for CodeMirror
        console.log("Initializing CodeMirror");
        codeEditor = CodeMirror(codeEditorElement, {
            mode: "javascript", // Default to JavaScript syntax
            theme: "dracula", // Use a dark theme that matches our UI
            lineNumbers: true,
            readOnly: true,
            value: "Describe your prototype and click \"Generate Prototype\" to create code.",
            viewportMargin: Infinity,
            lineWrapping: true,
            styleActiveLine: true,
            matchBrackets: true
        });
        
        // Add dark theme styling
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .cm-editor {
                background-color: #1e1e1e !important;
                color: #e0e0e0 !important;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                height: 100%;
            }
            .cm-content {
                background-color: #1e1e1e !important;
            }
            .cm-gutters {
                background-color: #252525 !important;
                border-right: 1px solid #333 !important;
                color: #777 !important;
            }
            .cm-activeLine {
                background-color: rgba(255, 255, 255, 0.05) !important;
            }
            .cm-matchingBracket {
                color: #4CAF50 !important;
                font-weight: bold;
            }
        `;
        document.head.appendChild(styleElement);
        
        // Make sure the editor is refreshed to take full size
        setTimeout(() => {
            if (codeEditor) {
                codeEditor.refresh();
                console.log("CodeMirror refreshed after timeout");
            }
        }, 100);
        
        console.log("CodeMirror initialized successfully");
        return codeEditor;
    } catch (error) {
        console.error("Error initializing CodeMirror:", error);
        // Fallback to simple pre
        codeEditorElement.innerHTML = '<pre>Generated code will appear here...</pre>';
        return null;
    }
}

// Add a window load event handler to make sure all resources are fully loaded
window.addEventListener('load', function() {
    console.log("Window fully loaded, ensuring CodeMirror is initialized");
    
    // Try to initialize CodeMirror again if not initialized
    if (!codeEditor) {
        console.log("CodeMirror not initialized in DOMContentLoaded, trying again");
        initCodeMirror();
    } else {
        console.log("CodeMirror already initialized, refreshing");
        codeEditor.refresh();
    }
    
    // If there's already a session loaded, try to display its code again
    if (currentSessionId) {
        console.log("Current session detected, reloading:", currentSessionId);
        loadSession(currentSessionId);
    }
});

// Load sessions on page load
document.addEventListener('DOMContentLoaded', async () => {
    // We'll no longer automatically display saved code on initial page load
    console.log("DOM content loaded");
    
    await loadSessions();
    
    // Add event listeners with confirmation logging
    const generateBtn = document.getElementById('generate');
    const enhanceBtn = document.getElementById('enhance-prompt');
    const newSessionBtn = document.getElementById('new-session');
    const copyBtn = document.getElementById('copy-code');
    const downloadBtn = document.getElementById('download-code');
    const executeBtn = document.getElementById('push-to-zed');
    
    if (generateBtn) {
        generateBtn.addEventListener('click', generate);
        console.log("✅ Generate button event listener attached");
    } else {
        console.error("❌ Generate button not found");
    }
    
    if (enhanceBtn) {
        enhanceBtn.addEventListener('click', enhancePrompt);
        console.log("✅ Enhance prompt button event listener attached");
    } else {
        console.error("❌ Enhance prompt button not found");
    }
    
    if (newSessionBtn) {
        newSessionBtn.addEventListener('click', createNewSession);
        console.log("✅ New session button event listener attached");
    } else {
        console.error("❌ New session button not found");
    }
    
    if (copyBtn) {
        copyBtn.addEventListener('click', copyCode);
        console.log("✅ Copy code button event listener attached");
    } else {
        console.error("❌ Copy code button not found");
    }
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadCode);
        console.log("✅ Download code button event listener attached");
    } else {
        console.error("❌ Download code button not found");
    }
    
    if (executeBtn) {
        executeBtn.addEventListener('click', pushToZed);
        console.log("✅ Execute Code button event listener attached");
    } else {
        console.error("❌ Execute Code button not found");
    }
    
    // Add multimodal input listeners
    const imageUpload = document.getElementById('image-upload');
    const audioUpload = document.getElementById('audio-upload');
    const videoUpload = document.getElementById('video-upload');
    
    if (imageUpload) {
        imageUpload.addEventListener('change', (e) => handleFileSelection(e.target, 'image'));
    }
    if (audioUpload) {
        audioUpload.addEventListener('change', (e) => handleFileSelection(e.target, 'audio'));
    }
    if (videoUpload) {
        videoUpload.addEventListener('change', (e) => handleFileSelection(e.target, 'video'));
    }
    
    // Initialize speech recognition and add mic button listener
    initSpeechRecognition();
    const micButton = document.getElementById('mic-button');
    if (micButton) {
        micButton.addEventListener('click', toggleSpeechRecognition);
    }
    
    // Setup Remote Mode toggle - Make sure this runs after the DOM is fully loaded
    const remoteModeBtn = document.getElementById('remote-mode');
    if (remoteModeBtn) {
        remoteModeBtn.addEventListener('click', function() {
            toggleRemoteMode();
        });
        console.log("Remote Mode button found and event listener attached");
    } else {
        console.error("Remote Mode button not found in the DOM");
    }
    
    // Call initCodeMirror on page load
    initCodeMirror();
});

async function loadSessions() {
    try {
        const response = await fetch('http://localhost:5000/get_sessions', {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            console.error(`Error fetching sessions: ${response.status} ${response.statusText}`);
            return; // Exit early if we can't get sessions
        }
        
        const data = await response.json();
        
        // Make sure sessions is an array before using forEach
        if (!Array.isArray(data)) {
            console.error('Sessions data is not an array:', data);
            sessions = []; // Set to empty array
            return;
        }
        
        sessions = data;
        const sessionList = document.getElementById('session-list');
        if (!sessionList) {
            console.error('Session list element not found');
            return;
        }
        
        sessionList.innerHTML = '';
        
        sessions.forEach(session => {
            // Create the session item container
            const sessionDiv = document.createElement('div');
            sessionDiv.className = 'session-item';
            sessionDiv.dataset.id = session.id;
            
            // Create the session name that users can click to load the session
            const sessionContent = document.createElement('div');
            sessionContent.className = 'session-content';
            
            const sessionName = document.createElement('div');
            sessionName.className = 'session-name';
            
            // Use custom name if available, otherwise use default session name
            if (session.name) {
                sessionName.textContent = session.name;
            } else {
                sessionName.textContent = `Session ${session.id.slice(0,8)}`;
            }
            
            // Create the date display
            const sessionDate = document.createElement('div');
            sessionDate.className = 'session-date';
            
            // Format the date from created_at
            if (session.created_at) {
                try {
                    const date = new Date(session.created_at);
                    const now = new Date();
                    const diffTime = now - date;
                    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                    
                    if (diffDays === 0) {
                        // Today - show time
                        sessionDate.textContent = `Today at ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
                    } else if (diffDays === 1) {
                        // Yesterday
                        sessionDate.textContent = `Yesterday at ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
                    } else if (diffDays < 7) {
                        // This week - show day name
                        sessionDate.textContent = `${date.toLocaleDateString([], {weekday: 'long'})} at ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
                    } else {
                        // Older - show full date
                        sessionDate.textContent = date.toLocaleDateString([], {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }
                } catch (e) {
                    sessionDate.textContent = 'Date unknown';
                }
            } else {
                sessionDate.textContent = 'Date unknown';
            }
            
            // Assemble the session content
            sessionContent.appendChild(sessionName);
            sessionContent.appendChild(sessionDate);
            
            sessionContent.onclick = () => loadSession(session.id);
            
            // Create the actions menu with 3 dots
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'session-actions';
            
            const menuTrigger = document.createElement('button');
            menuTrigger.className = 'menu-trigger';
            menuTrigger.innerHTML = '⋮';
            menuTrigger.onclick = (e) => toggleSessionMenu(e, session.id);
            
            const dropdownMenu = document.createElement('div');
            dropdownMenu.className = 'dropdown-menu';
            dropdownMenu.id = `menu-${session.id}`;
            
            // Add rename option
            const renameItem = document.createElement('div');
            renameItem.className = 'dropdown-item';
            renameItem.textContent = 'Rename';
            renameItem.onclick = () => renameSession(session.id);
            
            // Add delete option
            const deleteItem = document.createElement('div');
            deleteItem.className = 'dropdown-item';
            deleteItem.textContent = 'Delete';
            deleteItem.onclick = () => deleteSession(session.id);
            
            // Assemble the dropdown menu
            dropdownMenu.appendChild(renameItem);
            dropdownMenu.appendChild(deleteItem);
            
            // Assemble the actions menu
            actionsDiv.appendChild(menuTrigger);
            actionsDiv.appendChild(dropdownMenu);
            
            // Assemble the session item
            sessionDiv.appendChild(sessionContent);
            sessionDiv.appendChild(actionsDiv);
            
            // Add to the session list
            sessionList.appendChild(sessionDiv);
        });
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

// Function to toggle the session menu
function toggleSessionMenu(event, sessionId) {
    event.stopPropagation(); // Prevent the click from loading the session
    
    // Close all other menus
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (menu.id !== `menu-${sessionId}`) {
            menu.classList.remove('visible');
        }
    });
    
    // Toggle this menu
    const menu = document.getElementById(`menu-${sessionId}`);
    menu.classList.toggle('visible');
    
    // Add a click event listener to the document to close the menu when clicking outside
    document.addEventListener('click', function closeMenu(e) {
        if (!menu.contains(e.target) && e.target !== event.currentTarget) {
            menu.classList.remove('visible');
            document.removeEventListener('click', closeMenu);
        }
    });
}

// Function to rename a session
async function renameSession(sessionId) {
    const newName = prompt('Enter a new name for this session:');
    if (!newName || newName.trim() === '') return;
    
    try {
        const response = await fetch(`http://localhost:5000/rename_session/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName.trim() })
        });
        
        if (response.ok) {
            // Update the session name in the UI
            const sessionElement = document.querySelector(`.session-item[data-id="${sessionId}"] .session-name`);
            if (sessionElement) {
                sessionElement.textContent = newName.trim();
            }
            showNotification('Session renamed successfully! ✏️', 'success');
        } else {
            showNotification('Failed to rename session', 'error');
        }
    } catch (error) {
        console.error('Error renaming session:', error);
        showNotification('Error renaming session: ' + error.message, 'error');
    }
    
    // Close the menu
    document.getElementById(`menu-${sessionId}`).classList.remove('visible');
}

// Function to delete a session
async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this session?')) return;
    
    try {
        const response = await fetch(`http://localhost:5000/delete_session/${sessionId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // If the deleted session was the current one, clear the UI
            if (sessionId === currentSessionId) {
                currentSessionId = null;
                document.getElementById('chat-messages').innerHTML = '';
                document.getElementById('code-output').innerHTML = '<pre id="code-display" style="width: 100%; height: 100%; overflow: auto; margin: 0; padding: 10px; background-color: #1e1e1e; color: #e0e0e0; font-family: \'Courier New\', monospace; white-space: pre-wrap; border-radius: 5px;">Describe your prototype and click "Generate Prototype" to create code.</pre>';
            }
            
            // Reload the sessions list
            await loadSessions();
            showNotification('Session deleted successfully! 🗑️', 'success');
        } else {
            showNotification('Failed to delete session', 'error');
        }
    } catch (error) {
        console.error('Error deleting session:', error);
        showNotification('Error deleting session: ' + error.message, 'error');
    }
}

async function createNewSession() {
    const response = await fetch('http://localhost:5000/create_session', { method: 'POST' });
    const newSession = await response.json();
    currentSessionId = newSession.id;
    
    // Generate an automatic name for the session
    const sessionName = `Session ${new Date().toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
    })}`;
    
    // Save the session name
    try {
        await fetch(`http://localhost:5000/rename_session/${currentSessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: sessionName })
        });
    } catch (error) {
        console.error('Error naming session:', error);
    }
    
    await loadSessions();
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('code-output').innerHTML = '<pre id="code-display" style="width: 100%; height: 100%; overflow: auto; margin: 0; padding: 10px; background-color: #1e1e1e; color: #e0e0e0; font-family: \'Courier New\', monospace; white-space: pre-wrap; border-radius: 5px;">Describe your prototype and click "Generate Prototype" to create code.</pre>';
}

async function loadSession(sessionId) {
    try {
        const response = await fetch(`http://localhost:5000/get_session/${sessionId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error(`Error loading session: ${response.status} ${response.statusText}`);
            return;
        }
        
        const session = await response.json();
        currentSessionId = session.id;
        
        // Update active class on session items
        const sessionItems = document.querySelectorAll('.session-item');
        sessionItems.forEach(item => {
            if (item.dataset.id === sessionId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // Clear and populate chat messages
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = '';
        
        if (session.messages && Array.isArray(session.messages)) {
            session.messages.forEach(message => {
                const msgDiv = document.createElement('div');
                msgDiv.className = `message ${message.sender === 'user' ? 'user-message' : 'system-message'}`;
                
                // For system messages that contain reasoning, add special formatting
                if (message.sender === 'system' && message.content.includes('Agent\'s Reasoning:')) {
                    msgDiv.className = 'message think-message thinking-container';
                    
                    // Simple parsing to find reasoning section
                    const parts = message.content.split('Agent\'s Reasoning:');
                    if (parts.length > 1) {
                        const reasoning = parts[1].trim();
                        msgDiv.innerHTML = `
                            <div class="thinking-header">
                                <span class="reasoning-title">Agent's Reasoning:</span>
                            </div>
                            <div class="thinking-content">
                                ${reasoning.split('\n').map(line => `<p>${line}</p>`).join('')}
                            </div>
                        `;
                    } else {
                        msgDiv.textContent = message.content;
                    }
                } else {
                    msgDiv.textContent = message.content;
                }
                
                chatMessages.appendChild(msgDiv);
            });
        }
        
        // Update code display
        if (session.code && session.code !== "Describe your prototype and click \"Generate Prototype\" to create code.") {
            console.log("Session has code, displaying it");
            displayCode(session.code);
            
            // Store in localStorage and global variable
            localStorage.setItem('vibeproto_last_code', session.code);
            lastGeneratedCode = session.code;
            
            // Force update as backup
            setTimeout(() => {
                console.log("Force updating code display from session");
                displayCode(session.code); // Use displayCode instead of direct manipulation
            }, 100);
        } else {
            console.log("No code in session, showing default message");
            displayCode('Describe your prototype and click "Generate Prototype" to create code.');
        }
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
        console.error('Error loading session:', error);
        showNotification(`Failed to load session: ${error.message}`, 'error');
    }
}

// Enhance prompt function
async function enhancePrompt() {
    console.log("ENHANCE PROMPT FUNCTION CALLED");
    const prompt = document.getElementById('prompt').value.trim();
    console.log("Prompt value:", prompt);
    
    if (!prompt) {
        showNotification('Please enter a prompt to enhance', 'info');
        return;
    }

    // Show loading state
    const enhanceButton = document.getElementById('enhance-prompt');
    const originalText = enhanceButton.textContent;
    enhanceButton.textContent = 'Enhancing...';
    enhanceButton.disabled = true;
    console.log("Button state updated, starting enhancement");

    // Add user message to show the original prompt
    const chatMessages = document.getElementById('chat-messages');
    const userMsg = document.createElement('div');
    userMsg.className = 'message user-message';
    userMsg.textContent = prompt;
    chatMessages.appendChild(userMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add thinking message
    const thinkingMsg = document.createElement('div');
    thinkingMsg.className = 'message think-message thinking-container';
    thinkingMsg.innerHTML = `
        <div class="thinking-header">
            <div class="thinking-dots"><span>.</span><span>.</span><span>.</span></div> 
            <span>Enhancing your prompt...</span>
        </div>
        <div class="thinking-content">
            <p>Making your prompt more detailed and specific...</p>
        </div>
    `;
    chatMessages.appendChild(thinkingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    console.log("UI elements added");

    try {
        console.log("Remote mode:", remoteMode);
        if (remoteMode) {
            console.log("Using remote enhancement");
            // Use remote enhancement
            const response = await fetch('http://localhost:5000/remote_enhance_prompt', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    prompt,
                    session_id: currentSessionId,
                    user_id: userId
                }),
                mode: 'cors'
            });

            console.log("Remote enhance response status:", response.status);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const result = await response.json();
            console.log("Remote enhance result:", result);
            
            // Add to active tasks
            activeRemoteTasks[result.task_id] = {
                type: 'enhance_prompt',
                prompt: prompt
            };
            
            // Start checking for status
            startTaskStatusChecker();
            
            // Add a waiting message
            const chatMessages = document.getElementById('chat-messages');
            const waitingMsg = document.createElement('div');
            waitingMsg.className = 'message system-message';
            waitingMsg.textContent = 'Enhancing prompt in the background. You can continue using the application.';
            chatMessages.appendChild(waitingMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
        } else {
            console.log("Using direct enhancement");
            // Use direct enhancement
            const response = await fetch('http://localhost:5000/enhance_prompt', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt }),
                mode: 'cors'
            });

            console.log("Direct enhance response status:", response.status);
            console.log("Direct enhance response:", response);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error("Error response data:", errorData);
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const result = await response.json();
            console.log('Enhanced prompt result:', result);

            if (!result.enhanced_prompt) {
                throw new Error('No enhanced prompt received from server');
            }

            console.log("Updating prompt field with enhanced prompt");
            // Update the prompt with enhanced version
            document.getElementById('prompt').value = result.enhanced_prompt;
            
            // Also display in chat messages as a system message
            const chatMessages = document.getElementById('chat-messages');
            
            // Remove the thinking message first
            if (thinkingMsg && thinkingMsg.parentNode) {
                chatMessages.removeChild(thinkingMsg);
            }
            
            const enhanceMsg = document.createElement('div');
            enhanceMsg.className = 'message think-message thinking-container';
            enhanceMsg.innerHTML = `
                <div class="thinking-header">
                    <span class="reasoning-title">Enhanced Prompt:</span>
                </div>
                <div class="thinking-content">
                    ${result.enhanced_prompt.split('\n').map(line => `<p>${line}</p>`).join('')}
                </div>
            `;
            chatMessages.appendChild(enhanceMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Add a simple notification
            const notificationMsg = document.createElement('div');
            notificationMsg.className = 'message system-message';
            notificationMsg.textContent = '✅ Prompt enhanced successfully! You can now generate code with it.';
            chatMessages.appendChild(notificationMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            console.log("Enhancement completed successfully");
            // Reset button state for immediate mode
            enhanceButton.textContent = originalText;
            enhanceButton.disabled = false;
        }
    } catch (error) {
        console.error('Error enhancing prompt:', error);
        showNotification(`Error enhancing prompt: ${error.message}`, 'error');
        
        // Reset button state
        enhanceButton.textContent = originalText;
        enhanceButton.disabled = false;
    }
}

// The generate function (restored)
async function generate() {
    if (!currentSessionId) {
        await createNewSession();
    }

    const prompt = document.getElementById('prompt').value.trim();
    const prototypeType = document.getElementById('prototype-type').value;
    if (!prompt) {
        showNotification('Please enter a prompt to generate code', 'info');
        return;
    }

    // Show loading state
    const generateButton = document.getElementById('generate');
    const originalText = generateButton.textContent;
    generateButton.textContent = 'Generating...';
    generateButton.disabled = true;

    // Show loading animation in code area
    showLoadingInCodeArea();

    // Add user message
    const chatMessages = document.getElementById('chat-messages');
    const userMsg = document.createElement('div');
    userMsg.className = 'message user-message';
    userMsg.textContent = prompt;
    chatMessages.appendChild(userMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Show thinking indicator with custom text to simulate thinking process
    const thinkingMsg = document.createElement('div');
    thinkingMsg.className = 'message think-message thinking-container';
    thinkingMsg.innerHTML = `
        <div class="thinking-header">
            <div class="thinking-dots"><span>.</span><span>.</span><span>.</span></div> 
            <span>Agent is thinking...</span>
        </div>
        <div class="thinking-content" id="thinking-content">
            <p>Analyzing your request: "${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}"</p>
        </div>
    `;
    chatMessages.appendChild(thinkingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Simulate thinking process with staged updates for both remote and direct modes
    const thinkingContent = thinkingMsg.querySelector('#thinking-content');
    const thinkingStages = [
        "Determining the requirements for the " + prototypeType + "...",
        "Planning the architecture and components...",
        "Considering best practices and coding standards...",
        "Finalizing implementation approach..."
    ];
    
    let stageIndex = 0;
    const thinkingInterval = setInterval(() => {
        if (stageIndex < thinkingStages.length) {
            const stageElem = document.createElement('p');
            stageElem.textContent = thinkingStages[stageIndex];
            thinkingContent.appendChild(stageElem);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            stageIndex++;
        } else {
            clearInterval(thinkingInterval);
        }
    }, 2000); // Update every 2 seconds

    try {
        if (remoteMode) {
            // Use remote code generation
            const multimodalInput = getActiveMultimodalInput();
            const response = await fetch('http://localhost:5000/remote_generate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt,
                    type: prototypeType,
                    user_id: userId,
                    multimodal_input: multimodalInput ? {[multimodalInput.type]: multimodalInput.data.base64} : null
                }),
                mode: 'cors'
            });
            
            // Clear thinking interval
            clearInterval(thinkingInterval);
            
            const result = await response.json();
            if (result.error) {
                // Remove thinking indicator on error
                chatMessages.removeChild(thinkingMsg);
                showNotification(result.error, 'error');
                return;
            }
            
            // Update the thinking message
            thinkingMsg.innerHTML = `
                <div class="thinking-header">
                    <span class="reasoning-title">Task submitted for background processing</span>
                </div>
                <div class="thinking-content">
                    <p>Your request has been submitted to a remote agent.</p>
                    <p>Task ID: ${result.task_id}</p>
                    <p>You can continue using the application while the agent works in the background.</p>
                </div>
            `;
            
            // Add to active tasks
            activeRemoteTasks[result.task_id] = {
                type: 'generate_code',
                prompt: prompt,
                prototype_type: prototypeType
            };
            
            // Update current session
            currentSessionId = result.session_id;
            
            // Start checking for status
            startTaskStatusChecker();
            
        } else {
            // Use direct code generation
            const multimodalInput = getActiveMultimodalInput();
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt,
                    type: prototypeType,
                    session_id: currentSessionId,
                    user_id: userId,
                    think: true, // Always enable thinking
                    multimodal_input: multimodalInput ? {[multimodalInput.type]: multimodalInput.data.base64} : null
                }),
                mode: 'cors'
            });
            
            // Clear thinking interval
            clearInterval(thinkingInterval);
            
            const result = await response.json();
            if (result.error) {
                // Remove thinking indicator on error
                chatMessages.removeChild(thinkingMsg);
                showNotification(`Error generating code: ${result.error}`, 'error');
                return;
            }

            // Update the thinking message with actual reasoning if available
            if (result.reasoning) {
                thinkingMsg.innerHTML = `
                    <div class="thinking-header">
                        <span class="reasoning-title">Agent's Reasoning:</span>
                    </div>
                    <div class="thinking-content">
                        ${result.reasoning.split('\n').map(line => `<p>${line}</p>`).join('')}
                    </div>
                `;
            } else {
                // Remove thinking indicator if no reasoning is available
                chatMessages.removeChild(thinkingMsg);
            }

            // Display the generated code directly
            if (result && result.code) {
                console.log("Setting code from direct generation");
                
                // Store the code in localStorage as a backup
                if (result.code !== "Describe your prototype and click \"Generate Prototype\" to create code.") {
                    localStorage.setItem('vibeproto_last_code', result.code);
                    lastGeneratedCode = result.code;
                }
                
                // Use our direct display function with multiple fallbacks
                displayCode(result.code);
            } else {
                console.warn("Generation did not return any code");
            }

            // Add system response
            const sysMsg = document.createElement('div');
            sysMsg.className = 'message system-message';
            sysMsg.textContent = "Generated successfully!";
            chatMessages.appendChild(sysMsg);

            // Clear the prompt input
            document.getElementById('prompt').value = '';
            
            // Refresh session data
            await loadSession(currentSessionId);
            
            // Reset button state
            generateButton.textContent = originalText;
            generateButton.disabled = false;
        }
    } catch (error) {
        // Clear the thinking interval
        clearInterval(thinkingInterval);
        
        // Remove thinking indicator on error
        if (thinkingMsg.parentNode) {
            chatMessages.removeChild(thinkingMsg);
        }
        showNotification('Error generating code: ' + error.message, 'error');
        
        // Reset button state
        generateButton.textContent = originalText;
        generateButton.disabled = false;
    }
}

function copyCode() {
    try {
        // Get code from our pre element
        const codeDisplayElement = document.getElementById('code-display');
        if (!codeDisplayElement) {
            throw new Error("Code display element not found");
        }
        
        let codeText = codeDisplayElement.textContent;
        
        // Check if we actually have code to copy
        if (!codeText || codeText === "Generated code will appear here...") {
            // Try to get from localStorage as backup
            codeText = localStorage.getItem('vibeproto_last_code');
            if (!codeText) {
                throw new Error("No code has been generated yet");
            }
        }
        
        // Use Clipboard API to copy text
        navigator.clipboard.writeText(codeText).then(() => {
            // Show a temporary success message
            const statusMsg = document.getElementById('status');
            statusMsg.textContent = "✅ Code copied to clipboard!";
            setTimeout(() => { 
                statusMsg.textContent = ""; 
            }, 2000);
        }).catch((err) => {
            throw new Error(`Could not copy to clipboard: ${err}`);
        });
    } catch (error) {
        console.error("Error copying code:", error);
        showNotification(error.message, 'error');
    }
}

function downloadCode() {
    try {
        // Get code from our pre element
        const codeDisplayElement = document.getElementById('code-display');
        if (!codeDisplayElement) {
            throw new Error("Code display element not found");
        }
        
        let codeText = codeDisplayElement.textContent;
        
        // Check if we actually have code to download
        if (!codeText || codeText === "Generated code will appear here...") {
            // Try to get from localStorage as backup
            codeText = localStorage.getItem('vibeproto_last_code');
            if (!codeText) {
                throw new Error("No code has been generated yet");
            }
        }

        // Detect file extension based on content
        let fileExtension = '.js'; // Default to JavaScript
        
        // Simple heuristic to detect language
        if (codeText.includes('<!DOCTYPE html>') || codeText.includes('<html>')) {
            fileExtension = '.html';
        } else if (codeText.includes('def ') && codeText.includes('import ')) {
            fileExtension = '.py';
        } else if (codeText.includes('@media') && codeText.includes('{') && codeText.includes('}')) {
            fileExtension = '.css';
        }
        
        // Create filename based on current time
        const date = new Date();
        const filename = `vibeproto_code_${date.getFullYear()}${(date.getMonth()+1).toString().padStart(2, '0')}${date.getDate().toString().padStart(2, '0')}_${date.getHours().toString().padStart(2, '0')}${date.getMinutes().toString().padStart(2, '0')}${fileExtension}`;
        
        // Create a download link
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(codeText));
        element.setAttribute('download', filename);
        
        // Hide element, add to DOM, click it, and remove it
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        // Show a temporary success message
        const statusMsg = document.getElementById('status');
        statusMsg.textContent = `✅ Code downloaded as ${filename}`;
        setTimeout(() => { 
            statusMsg.textContent = ""; 
        }, 3000);
    } catch (error) {
        console.error("Error downloading code:", error);
        showNotification(error.message, 'error');
    }
}

function analyzeCode() {
    if (codeEditor) {
        const code = codeEditor.getValue();
        if (!code || code === 'Generated code will appear here...') {
            alert('No code to analyze');
            return;
        }
        alert('Code analysis feature coming soon! Code length: ' + code.length + ' characters.');
    } else {
        alert('No code to analyze');
    }
}

// Settings Modal Management
const modal = document.getElementById('settings-modal');
const settingsBtn = document.getElementById('settings-btn');
const closeBtn = document.querySelector('.close-button');
const saveKeysBtn = document.getElementById('save-keys');

// API Key Management
const openaiKeyInput = document.getElementById('openai-key');
const anthropicKeyInput = document.getElementById('anthropic-key');
const openaiStatus = document.getElementById('openai-status');
const anthropicStatus = document.getElementById('anthropic-status');

// Show/hide modal
settingsBtn.onclick = () => {
    modal.style.display = "block";
    loadApiKeys();
};

closeBtn.onclick = () => {
    modal.style.display = "none";
};

window.onclick = (event) => {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};

// Load API keys from backend
async function loadApiKeys() {
    try {
        const response = await fetch('http://localhost:5000/get_api_keys');
        const keys = await response.json();
        
        if (keys.openai_key) {
            openaiKeyInput.value = "********";
            openaiStatus.textContent = "Set";
            openaiStatus.className = "status set";
        } else {
            openaiKeyInput.value = "";
            openaiStatus.textContent = "Not set";
            openaiStatus.className = "status not-set";
        }
        
        if (keys.anthropic_key) {
            anthropicKeyInput.value = "********";
            anthropicStatus.textContent = "Set";
            anthropicStatus.className = "status set";
        } else {
            anthropicKeyInput.value = "";
            anthropicStatus.textContent = "Not set";
            anthropicStatus.className = "status not-set";
        }
    } catch (error) {
        console.error('Error loading API keys:', error);
    }
}

// Save API keys
saveKeysBtn.onclick = async () => {
    const openaiKey = openaiKeyInput.value;
    const anthropicKey = anthropicKeyInput.value;
    
    try {
        const response = await fetch('http://localhost:5000/save_api_keys', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                openai_key: openaiKey === "********" ? null : openaiKey,
                anthropic_key: anthropicKey === "********" ? null : anthropicKey,
            }),
        });
        
        if (response.ok) {
            showNotification('API keys saved successfully! 🔑', 'success');
            loadApiKeys();  // Refresh the status
            modal.style.display = "none";
            location.reload();  // Reload the page to reinitialize with new keys
        } else {
            const error = await response.json();
            showNotification('Failed to save API keys: ' + error.error, 'error');
        }
    } catch (error) {
        console.error('Error saving API keys:', error);
        showNotification('Failed to save API keys. Please try again.', 'error');
    }
};

// Toggle Remote Mode function with enhanced visual feedback
function toggleRemoteMode() {
    remoteMode = !remoteMode;
    console.log("Toggle Remote Mode called, new state:", remoteMode);
    
    // Update button state
    const remoteModeBtn = document.getElementById('remote-mode');
    const remoteModeText = document.getElementById('remote-mode-text');
    const remoteModeIcon = document.getElementById('remote-mode-icon');
    
    if (remoteModeBtn && remoteModeText) {
        if (remoteMode) {
            // Update text
            remoteModeText.textContent = 'Remote Mode: ON';
            
            // Update button style
            remoteModeBtn.classList.add('active');
            
            // Update icon
            if (remoteModeIcon) {
                remoteModeIcon.textContent = '🛰️';
            }
            
            // Start background task checker
            startTaskStatusChecker();
            console.log("Remote Mode activated");
            
            // Add status message
            const status = document.getElementById('status');
            if (status) {
                status.textContent = '✅ Remote Mode active - tasks will continue in the background';
            }
        } else {
            // Update text
            remoteModeText.textContent = 'Remote Mode: OFF';
            
            // Update button style
            remoteModeBtn.classList.remove('active');
            
            // Update icon
            if (remoteModeIcon) {
                remoteModeIcon.textContent = '🔄';
            }
            
            // Stop background task checker
            stopTaskStatusChecker();
            console.log("Remote Mode deactivated");
            
            // Update status message
            const status = document.getElementById('status');
            if (status) {
                status.textContent = 'Remote Mode disabled - using standard processing';
            }
        }
    } else {
        console.error("Could not find one or more remote mode elements");
    }
}

function startTaskStatusChecker() {
    if (taskStatusCheckInterval) return;
    
    taskStatusCheckInterval = setInterval(checkPendingTasks, 5000);
    console.log("Task status checker started");
}

function stopTaskStatusChecker() {
    if (taskStatusCheckInterval) {
        clearInterval(taskStatusCheckInterval);
        taskStatusCheckInterval = null;
        console.log("Task status checker stopped");
    }
}

function checkPendingTasks() {
    const taskIds = Object.keys(activeRemoteTasks);
    if (!taskIds.length) return;
    
    taskIds.forEach(async (taskId) => {
        try {
            const response = await fetch(`http://localhost:5000/get_remote_task_status/${taskId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const taskStatus = await response.json();
            
            if (taskStatus.status === 'completed' || taskStatus.status === 'failed') {
                handleTaskCompletion(taskId, taskStatus);
            }
        } catch (error) {
            console.error(`Error checking task ${taskId}:`, error);
        }
    });
}

function handleTaskCompletion(taskId, taskStatus) {
    const taskInfo = activeRemoteTasks[taskId];
    if (!taskInfo) return;
    
    // Remove from active tasks
    delete activeRemoteTasks[taskId];
    
    // If no more active tasks, we can stop checking
    if (!Object.keys(activeRemoteTasks).length) {
        stopTaskStatusChecker();
    }
    
    // Handle task completion based on type
    if (taskInfo.type === 'enhance_prompt') {
        handleRemoteEnhanceResult(taskStatus);
    } else if (taskInfo.type === 'generate_code') {
        handleRemoteGenerateResult(taskStatus);
        
        // Emergency check - force code to display if not showing
        setTimeout(() => {
            const editorValue = codeEditor ? codeEditor.getValue() : "";
            const result = taskStatus.result || {};
            
            if (result.code && editorValue === "Generated code will appear here...") {
                console.log("EMERGENCY FIX: Code not displayed properly, forcing display");
                ensureCodeIsDisplayed(result.code);
            }
        }, 500);
    }
}

function handleRemoteEnhanceResult(taskStatus) {
    const enhanceButton = document.getElementById('enhance-prompt');
    enhanceButton.textContent = 'Enhance Prompt';
    enhanceButton.disabled = false;
    
    if (taskStatus.error) {
        showNotification(`Error enhancing prompt: ${taskStatus.error}`, 'error');
        return;
    }
    
    if (taskStatus.result && taskStatus.result.enhanced_prompt) {
        // Update the prompt with enhanced version
        document.getElementById('prompt').value = taskStatus.result.enhanced_prompt;
        
        // Also display in chat messages as a system message
        const chatMessages = document.getElementById('chat-messages');
        const enhanceMsg = document.createElement('div');
        enhanceMsg.className = 'message think-message thinking-container';
        enhanceMsg.innerHTML = `
            <div class="thinking-header">
                <span class="reasoning-title">Enhanced Prompt:</span>
            </div>
            <div class="thinking-content">
                ${taskStatus.result.enhanced_prompt.split('\n').map(line => `<p>${line}</p>`).join('')}
            </div>
        `;
        chatMessages.appendChild(enhanceMsg);
        
        // Add a simple notification
        const notificationMsg = document.createElement('div');
        notificationMsg.className = 'message system-message';
        notificationMsg.textContent = '✅ Prompt enhanced successfully! You can now generate code with it.';
        chatMessages.appendChild(notificationMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function handleRemoteGenerateResult(taskStatus) {
    const generateButton = document.getElementById('generate');
    generateButton.textContent = 'Generate';
    generateButton.disabled = false;
    
    if (taskStatus.error) {
        showNotification(`Error generating code: ${taskStatus.error}`, 'error');
        return;
    }
    
    // Get the result data
    const result = taskStatus.result;
    
    // Display the generated code directly
    if (result && result.code) {
        console.log("Setting code from remote generation");
        
        // Store the code in localStorage as a backup
        if (result.code !== "Describe your prototype and click \"Generate Prototype\" to create code.") {
            localStorage.setItem('vibeproto_last_code', result.code);
            lastGeneratedCode = result.code;
        }
        
        // Use our direct display function
        displayCode(result.code);
    } else {
        console.warn("Remote generation did not return any code");
    }
    
    // Add reasoning if available
    if (result && result.reasoning) {
        const chatMessages = document.getElementById('chat-messages');
        const thinkingMsg = document.createElement('div');
        thinkingMsg.className = 'message think-message thinking-container';
        thinkingMsg.innerHTML = `
            <div class="thinking-header">
                <span class="reasoning-title">Agent's Reasoning:</span>
            </div>
            <div class="thinking-content">
                ${result.reasoning.split('\n').map(line => `<p>${line}</p>`).join('')}
            </div>
        `;
        chatMessages.appendChild(thinkingMsg);
    }
    
    // Add system response
    const chatMessages = document.getElementById('chat-messages');
    const sysMsg = document.createElement('div');
    sysMsg.className = 'message system-message';
    sysMsg.textContent = "Generated successfully!";
    chatMessages.appendChild(sysMsg);
    
    // Clear the prompt input
    document.getElementById('prompt').value = '';
    
    // Refresh session data if we have a session ID
    if (result && result.session_id) {
        loadSession(result.session_id);
    }
}

// This function will directly display code in the pre element
function displayCode(code) {
    if (!code) {
        code = "Describe your prototype and click \"Generate Prototype\" to create code.";
    }
    
    console.log("DISPLAYING CODE DIRECTLY:", code.substring(0, 50) + "...");
    
    // Save to localStorage for persistence
    if (code && code !== "Describe your prototype and click \"Generate Prototype\" to create code.") {
        localStorage.setItem('vibeproto_last_code', code);
        lastGeneratedCode = code;
    }
    
    // Generate instructions for the code
    const instructions = generateDetailedInstructions(code);
    
    // Get the code container
    const codeContainer = document.getElementById('code-output');
    if (codeContainer) {
        // Escape HTML in code to prevent parsing issues
        const escapedCode = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        // Create new structure with code and instructions
        codeContainer.innerHTML = `
            <div class="code-display-container">
                <pre id="code-display" style="width: 100%; overflow: auto; margin: 0; padding: 10px; background-color: #1e1e1e; color: #e0e0e0; font-family: 'Courier New', monospace; white-space: pre-wrap; border-radius: 5px; max-height: 60vh;">${escapedCode}</pre>
                <div class="code-instructions">
                    <h4>📋 Step-by-Step Instructions for Non-Technical Users</h4>
                    ${instructions}
                </div>
            </div>
        `;
        
        // Debug: Log what we're displaying
        console.log("Code container updated with:", escapedCode.substring(0, 100) + "...");
        
        // Double-check the element exists and has content
        const newCodeDisplay = document.getElementById('code-display');
        if (newCodeDisplay) {
            console.log("Code display element created successfully with content length:", newCodeDisplay.textContent.length);
        } else {
            console.error("Failed to create code-display element");
        }
    } else {
        console.error("Could not find code-output container");
        
        // Fallback: try to find the original code-display element
        const fallbackElement = document.getElementById('code-display');
        if (fallbackElement) {
            console.log("Using fallback code display element");
            fallbackElement.textContent = code;
        }
    }
}

function generateDetailedInstructions(code) {
    if (!code || code === "Describe your prototype and click \"Generate Prototype\" to create code.") {
        return "<p>No instructions available yet. Generate some code first!</p>";
    }
    
    // Detect code type
    const isHTML = code.includes('<!DOCTYPE') || code.includes('<html') || code.includes('<div') || code.includes('<script>');
    const isPython = code.includes('def ') || code.includes('import ') || code.includes('print(') || code.includes('if __name__');
    const isJavaScript = code.includes('function ') || code.includes('const ') || code.includes('let ') || code.includes('console.log');
    
    let instructions = '';
    
    if (isHTML) {
        instructions = `
            <p><strong>🌐 You've generated a Web Application!</strong> Here's how to run it using Cursor:</p>
            
            <div class="instruction-steps">
                <h5>Step 1: Save the Code</h5>
                <ol>
                    <li>Click the <strong>"Copy Code"</strong> button above</li>
                    <li>Open <strong>Cursor</strong> (your AI-powered code editor)</li>
                    <li>Create a new file: <code>Ctrl+N</code> (Windows) or <code>Cmd+N</code> (Mac)</li>
                    <li>Paste the code: <code>Ctrl+V</code> (Windows) or <code>Cmd+V</code> (Mac)</li>
                    <li>Save the file with a <code>.html</code> extension (e.g., <code>my-app.html</code>)</li>
                </ol>
                
                <h5>Step 2: Run Your Web App</h5>
                <ol>
                    <li>In Cursor, right-click on your HTML file in the file explorer</li>
                    <li>Select <strong>"Open with Live Server"</strong> or <strong>"Open in Browser"</strong></li>
                    <li>If you don't see this option, install the "Live Server" extension in Cursor</li>
                    <li>Your web app will open in your default browser automatically!</li>
                </ol>
                
                <h5>Step 3: Make Changes (Optional)</h5>
                <ol>
                    <li>Go back to Cursor and modify the code</li>
                    <li>Save the file (<code>Ctrl+S</code> or <code>Cmd+S</code>)</li>
                    <li>The browser will automatically refresh to show your changes</li>
                    <li>Ask Cursor's AI for help: Press <code>Ctrl+K</code> and describe what you want to change</li>
                </ol>
                
                <h5>🎯 What This Code Does:</h5>
                <p>This is a complete web application that runs in your browser. It includes:</p>
                <ul>
                    <li><strong>HTML</strong>: The structure and content of your app</li>
                    <li><strong>CSS</strong>: The styling and visual design</li>
                    <li><strong>JavaScript</strong>: The interactive functionality</li>
                </ul>
                
                <h5>🔧 Troubleshooting:</h5>
                <ul>
                    <li><strong>File won't open?</strong> Make sure you saved it with a <code>.html</code> extension</li>
                    <li><strong>No Live Server?</strong> Go to Extensions in Cursor and install "Live Server"</li>
                    <li><strong>App looks broken?</strong> Check the browser console (F12) for error messages</li>
                    <li><strong>Need help?</strong> Ask Cursor's AI: "Help me fix this HTML code"</li>
                </ul>
            </div>
        `;
    } else if (isPython) {
        instructions = `
            <p><strong>🐍 You've generated a Python Script!</strong> Here's how to run it using Cursor:</p>
            
            <div class="instruction-steps">
                <h5>Step 1: Save the Code</h5>
                <ol>
                    <li>Click the <strong>"Copy Code"</strong> button above</li>
                    <li>Open <strong>Cursor</strong> (your AI-powered code editor)</li>
                    <li>Create a new file: <code>Ctrl+N</code> (Windows) or <code>Cmd+N</code> (Mac)</li>
                    <li>Paste the code: <code>Ctrl+V</code> (Windows) or <code>Cmd+V</code> (Mac)</li>
                    <li>Save the file with a <code>.py</code> extension (e.g., <code>my-script.py</code>)</li>
                </ol>
                
                <h5>Step 2: Install Python (if needed)</h5>
                <ol>
                    <li>Check if Python is installed: Open Terminal in Cursor (<code>Ctrl+\`</code>)</li>
                    <li>Type <code>python --version</code> and press Enter</li>
                    <li>If you see a version number (like 3.9.x), you're good to go!</li>
                    <li>If not, download Python from <code>python.org</code> and install it</li>
                </ol>
                
                <h5>Step 3: Install Required Packages</h5>
                <ol>
                    <li>Look at the top of your code for <code>import</code> statements</li>
                    <li>In Cursor's Terminal, install packages with: <code>pip install package-name</code></li>
                    <li>Common commands:
                        <ul>
                            <li><code>pip install requests</code> (for web requests)</li>
                            <li><code>pip install beautifulsoup4</code> (for web scraping)</li>
                            <li><code>pip install pandas</code> (for data handling)</li>
                        </ul>
                    </li>
                </ol>
                
                <h5>Step 4: Run Your Script</h5>
                <ol>
                    <li>In Cursor's Terminal, navigate to your file's folder</li>
                    <li>Run the script: <code>python my-script.py</code></li>
                    <li>Follow any prompts the script shows you</li>
                    <li>Watch the magic happen! 🎉</li>
                </ol>
                
                <h5>Step 5: Customize and Improve</h5>
                <ol>
                    <li>Use Cursor's AI to modify the script: Press <code>Ctrl+K</code></li>
                    <li>Ask questions like: "Make this faster" or "Add error handling"</li>
                    <li>Test your changes by running the script again</li>
                </ol>
                
                <h5>🎯 What This Script Does:</h5>
                <p>This Python script automates a task for you. It can:</p>
                <ul>
                    <li>Process files and data automatically</li>
                    <li>Connect to websites and APIs</li>
                    <li>Organize and manipulate information</li>
                    <li>Save you hours of manual work</li>
                </ul>
                
                <h5>🔧 Troubleshooting:</h5>
                <ul>
                    <li><strong>Import errors?</strong> Install missing packages with <code>pip install package-name</code></li>
                    <li><strong>Script won't run?</strong> Check you're in the right folder in Terminal</li>
                    <li><strong>Python not found?</strong> Try <code>python3</code> instead of <code>python</code></li>
                    <li><strong>Need help?</strong> Ask Cursor's AI: "Help me fix this Python error"</li>
                </ul>
            </div>
        `;
    } else if (isJavaScript) {
        instructions = `
            <p><strong>⚡ You've generated JavaScript Code!</strong> Here's how to run it using Cursor:</p>
            
            <div class="instruction-steps">
                <h5>Step 1: Save the Code</h5>
                <ol>
                    <li>Click the <strong>"Copy Code"</strong> button above</li>
                    <li>Open <strong>Cursor</strong> (your AI-powered code editor)</li>
                    <li>Create a new file: <code>Ctrl+N</code> (Windows) or <code>Cmd+N</code> (Mac)</li>
                    <li>Paste the code: <code>Ctrl+V</code> (Windows) or <code>Cmd+V</code> (Mac)</li>
                    <li>Save the file with a <code>.js</code> extension (e.g., <code>my-script.js</code>)</li>
                </ol>
                
                <h5>Step 2: Run with Node.js</h5>
                <ol>
                    <li>Install Node.js from <code>nodejs.org</code> if you haven't already</li>
                    <li>Open Terminal in Cursor (<code>Ctrl+\`</code>)</li>
                    <li>Navigate to your file's location</li>
                    <li>Run: <code>node my-script.js</code></li>
                </ol>
                
                <h5>Step 3: Alternative - Run in Browser</h5>
                <ol>
                    <li>Create an HTML file to host your JavaScript</li>
                    <li>Add your JS code between <code>&lt;script&gt;</code> tags</li>
                    <li>Open the HTML file in your browser</li>
                    <li>Check the browser console (F12) to see output</li>
                </ol>
                
                <h5>🎯 What This Code Does:</h5>
                <p>This JavaScript code can run in browsers or with Node.js to:</p>
                <ul>
                    <li>Process data and perform calculations</li>
                    <li>Interact with web pages and APIs</li>
                    <li>Create interactive user experiences</li>
                    <li>Automate repetitive tasks</li>
                </ul>
            </div>
        `;
    } else {
        // Generic instructions for unknown code types
        instructions = `
            <p><strong>💻 You've generated some code!</strong> Here's how to work with it in Cursor:</p>
            
            <div class="instruction-steps">
                <h5>Step 1: Save the Code</h5>
                <ol>
                    <li>Click the <strong>"Copy Code"</strong> button above</li>
                    <li>Open <strong>Cursor</strong> (your AI-powered code editor)</li>
                    <li>Create a new file: <code>Ctrl+N</code> (Windows) or <code>Cmd+N</code> (Mac)</li>
                    <li>Paste the code: <code>Ctrl+V</code> (Windows) or <code>Cmd+V</code> (Mac)</li>
                    <li>Save with an appropriate file extension (ask Cursor's AI if unsure)</li>
                </ol>
                
                <h5>Step 2: Get Help from Cursor's AI</h5>
                <ol>
                    <li>Press <code>Ctrl+K</code> (Windows) or <code>Cmd+K</code> (Mac)</li>
                    <li>Ask: "How do I run this code?"</li>
                    <li>Cursor's AI will provide specific instructions for your code type</li>
                </ol>
                
                <h5>Step 3: Run Your Code</h5>
                <ol>
                    <li>Follow the AI's recommendations for your specific language</li>
                    <li>Use Cursor's built-in Terminal if needed</li>
                    <li>Install any required dependencies the AI suggests</li>
                </ol>
            </div>
        `;
    }
    
    // Add universal tips
    instructions += `
        <div class="cursor-tips">
            <h5>💡 Pro Tips for Using Cursor:</h5>
            <ul>
                <li><strong>Ask AI for help:</strong> Press <code>Ctrl+K</code> (or <code>Cmd+K</code>) and describe what you want</li>
                <li><strong>Explain code:</strong> Select any code and ask "What does this do?"</li>
                <li><strong>Fix errors:</strong> If you see red squiggly lines, right-click and select "Fix with AI"</li>
                <li><strong>Improve code:</strong> Ask "Make this code better" or "Add comments to explain this"</li>
                <li><strong>Quick reference:</strong> Hover over any function or variable to see what it does</li>
            </ul>
        </div>
        
        <div class="execution-reminder">
            <p><strong>🚀 Ready to Execute?</strong> Click the <strong>"Execute Code"</strong> button above to run your code directly, or follow the manual steps for more control!</p>
        </div>
    `;
    
    return instructions;
}

// Replace the previous functions with our simplified version
function forceDisplayCode(code) {
    console.log("FORCE DISPLAYING CODE:", code.substring(0, 50) + "...");
    displayCode(code); // Use the main displayCode function which now handles everything
}

function ensureCodeIsDisplayed(code) {
    displayCode(code); // Use the main displayCode function which now handles everything
}

// Function to push code to Zed IDE - with error handling improvements
async function pushToZed() {
    console.log("Execute Code button clicked!");
    
    try {
        let codeText = "";
        
        // Get the code from our pre element
        const codeDisplayElement = document.getElementById('code-display');
        if (codeDisplayElement) {
            codeText = codeDisplayElement.textContent;
            console.log("Got code from code-display element, length:", codeText.length);
        } else {
            console.log("No code-display element found");
        }
        
        // Also check localStorage as a backup
        if (!codeText || codeText === "Describe your prototype and click \"Generate Prototype\" to create code.") {
            codeText = localStorage.getItem('vibeproto_last_code');
            console.log("Using localStorage backup code, length:", codeText ? codeText.length : 0);
            if (!codeText) {
                showNotification('No code available to execute. Generate some code first!', 'error');
                return;
            }
        }
        
        console.log("Executing code, length:", codeText.length);
        console.log("First 100 chars:", codeText.substring(0, 100));
        
        // Check if this is HTML content
        const isHTML = codeText.includes('<!DOCTYPE') || codeText.includes('<html>');
        console.log("Is HTML content:", isHTML);
        
        if (isHTML) {
            console.log("HTML content detected, adding special handling");
            
            // Create an object with file info to help the server
            const payload = {
                code: codeText,
                fileType: "html",
                fileName: "index.html"
            };
            
            console.log("Sending HTML payload to server...");
            
            // Send the code to the backend with file info
            const response = await fetch('http://localhost:5000/push_to_zed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload),
                mode: 'cors'
            });
            
            console.log("Server response status:", response.status);
            
            // Check response
            if (response.ok) {
                const result = await response.json();
                console.log("Server response:", result);
                showNotification('HTML application opened in browser successfully! 🚀', 'success');
            } else {
                const errorText = await response.text();
                console.error("Server error:", errorText);
                showNotification(`Failed to execute code: ${errorText}`, 'error');
            }
        } else {
            console.log("Non-HTML content, using normal approach");
            
            // For non-HTML content, use the normal approach
            const response = await fetch('http://localhost:5000/push_to_zed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code: codeText }),
                mode: 'cors'
            });
            
            console.log("Server response status:", response.status);
            
            // Check for JSON response
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                const result = await response.json();
                console.log("Server JSON response:", result);
                
                if (response.ok) {
                    if (result.output) {
                        showNotification(`Code executed successfully! Output: ${result.output.substring(0, 100)}`, 'success');
                    } else {
                        showNotification(result.message || 'Code executed successfully! ✨', 'success');
                    }
                } else {
                    showNotification(result.error || 'Failed to execute code', 'error');
                }
            } else {
                // Handle non-JSON response
                const textResult = await response.text();
                console.log("Server text response:", textResult);
                if (response.ok) {
                    showNotification('Code executed successfully! 🎉', 'success');
                } else {
                    showNotification(`Server error: ${textResult}`, 'error');
                }
            }
        }
    } catch (error) {
        console.error('Error executing code:', error);
        showNotification(`Error executing code: ${error.message}`, 'error');
    }
}

// Remove auto-loading of code from localStorage on page load
document.addEventListener('DOMContentLoaded', () => {
    // Only add observer for "Generated successfully" message
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.textContent && node.textContent.includes("Generated successfully")) {
                            console.log("SUCCESS MESSAGE DETECTED, USING SAVED CODE");
                            
                            // Check what's currently displayed in the code area
                            const codeDisplayElement = document.getElementById('code-display');
                            const currentDisplayedCode = codeDisplayElement ? codeDisplayElement.textContent : "";
                            
                            // Only update if it's not showing code yet
                            if (!currentDisplayedCode || 
                                currentDisplayedCode === "Describe your prototype and click \"Generate Prototype\" to create code." ||
                                currentDisplayedCode === "Generated code will appear here...") {
                                
                                console.log("Code display needs update after success message");
                                
                                // Use the most recent code we have
                                if (lastGeneratedCode) {
                                    setTimeout(() => {
                                        displayCode(lastGeneratedCode); // Use displayCode instead of forceDisplayCode
                                    }, 100);
                                } else if (localStorage.getItem('vibeproto_last_code')) {
                                    const savedCode = localStorage.getItem('vibeproto_last_code');
                                    setTimeout(() => {
                                        displayCode(savedCode); // Use displayCode instead of forceDisplayCode
                                    }, 100);
                                }
                            } else {
                                console.log("Code already displayed, no need to update");
                            }
                        }
                    });
                }
            });
        });

        observer.observe(chatMessages, { childList: true, subtree: true });
    }
}); 