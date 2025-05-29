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
    document.getElementById('generate').addEventListener('click', generate);
    document.getElementById('enhance-prompt').addEventListener('click', enhancePrompt);
    document.getElementById('new-session').addEventListener('click', createNewSession);
    document.getElementById('copy-code').addEventListener('click', copyCode);
    document.getElementById('download-code').addEventListener('click', downloadCode);
    document.getElementById('push-to-zed').addEventListener('click', pushToZed);
    
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
            method: 'GET',
            headers: {
                'Access-Control-Allow-Origin': '*'
            },
            mode: 'cors'
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
            const sessionName = document.createElement('div');
            sessionName.className = 'session-name';
            
            // Use custom name if available, otherwise use default session name
            if (session.name) {
                sessionName.textContent = session.name;
            } else {
                sessionName.textContent = `Session ${session.id.slice(0,8)}`;
            }
            
            sessionName.onclick = () => loadSession(session.id);
            
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
            sessionDiv.appendChild(sessionName);
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
                'Access-Control-Allow-Origin': '*'
            },
            mode: 'cors'
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
        if (session.code) {
            console.log("Loading code from session");
            
            // Store in localStorage for backup
            if (session.code !== "Describe your prototype and click \"Generate Prototype\" to create code.") {
                localStorage.setItem('vibeproto_last_code', session.code);
                lastGeneratedCode = session.code;
            }
            
            // Use our direct display function 
            displayCode(session.code);
            
            // Force update with delay to ensure it takes effect
            setTimeout(() => {
                console.log("Force updating code display from session");
                
                // Direct update to code display element
                const codeDisplayElement = document.getElementById('code-display');
                if (codeDisplayElement) {
                    codeDisplayElement.textContent = session.code;
                }
                
                // Update editor if available
                if (codeEditor) {
                    codeEditor.setValue(session.code);
                    codeEditor.refresh();
                }
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
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
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
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
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
            const response = await fetch('http://localhost:5000/remote_generate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    prompt,
                    type: prototypeType,
                    user_id: userId
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
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    prompt,
                    type: prototypeType,
                    session_id: currentSessionId,
                    user_id: userId,
                    think: true // Always enable thinking
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
                
                // Force display after a small delay to ensure it takes
                setTimeout(() => {
                    console.log("FORCE DISPLAYING CODE AFTER DELAY");
                    
                    // Get the pre element and update its content directly
                    const codeDisplayElement = document.getElementById('code-display');
                    if (codeDisplayElement) {
                        codeDisplayElement.textContent = result.code;
                    }
                    
                    // Also try to update the code editor if it exists
                    if (codeEditor) {
                        codeEditor.setValue(result.code);
                        codeEditor.refresh();
                    }
                }, 200);
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
                    'Access-Control-Allow-Origin': '*'
                },
                mode: 'cors'
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
        
        // Force display after a small delay to ensure it takes
        setTimeout(() => {
            console.log("FORCE DISPLAYING CODE AFTER DELAY");
            
            // Get the pre element and update its content directly
            const codeDisplayElement = document.getElementById('code-display');
            if (codeDisplayElement) {
                codeDisplayElement.textContent = result.code;
            }
            
            // Also try to update the code editor if it exists
            if (codeEditor) {
                codeEditor.setValue(result.code);
                codeEditor.refresh();
            }
        }, 200);
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
    
    // Get the pre element and update its content
    const codeDisplayElement = document.getElementById('code-display');
    if (codeDisplayElement) {
        codeDisplayElement.textContent = code;
    } else {
        console.error("Could not find code-display element");
    }
}

// Replace the previous functions with our simplified version
function forceDisplayCode(code) {
    displayCode(code);
}

function ensureCodeIsDisplayed(code) {
    displayCode(code);
}

// Function to push code to Zed IDE - with error handling improvements
async function pushToZed() {
    try {
        let codeText = "";
        
        // Get the code from our pre element
        const codeDisplayElement = document.getElementById('code-display');
        if (codeDisplayElement) {
            codeText = codeDisplayElement.textContent;
        }
        
        // Also check localStorage as a backup
        if (!codeText || codeText === "Describe your prototype and click \"Generate Prototype\" to create code.") {
            codeText = localStorage.getItem('vibeproto_last_code');
            if (!codeText) {
                showNotification('No code available to execute', 'error');
                return;
            }
        }
        
        console.log("Executing code, length:", codeText.length);
        
        // Check if this is HTML content
        const isHTML = codeText.includes('<!DOCTYPE') || codeText.includes('<html>');
        if (isHTML) {
            console.log("HTML content detected, adding special handling");
            
            // Create an object with file info to help the server
            const payload = {
                code: codeText,
                fileType: "html",
                fileName: "index.html"
            };
            
            // Send the code to the backend with file info
            const response = await fetch('http://localhost:5000/push_to_zed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify(payload),
                mode: 'cors'
            });
            
            // Check response
            if (response.ok) {
                const result = await response.json();
                showNotification('HTML application opened in browser successfully! 🚀', 'success');
            } else {
                const errorText = await response.text();
                showNotification(`Failed to execute code: ${errorText}`, 'error');
            }
        } else {
            // For non-HTML content, use the normal approach
            const response = await fetch('http://localhost:5000/push_to_zed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({ code: codeText }),
                mode: 'cors'
            });
            
            // Check for JSON response
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                const result = await response.json();
                
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
                                        forceDisplayCode(lastGeneratedCode);
                                        
                                        // Double-check and force direct update if needed
                                        setTimeout(() => {
                                            if (codeDisplayElement && codeDisplayElement.textContent !== lastGeneratedCode) {
                                                console.log("EMERGENCY CODE DISPLAY UPDATE");
                                                codeDisplayElement.textContent = lastGeneratedCode;
                                            }
                                        }, 300);
                                    }, 100);
                                } else if (localStorage.getItem('vibeproto_last_code')) {
                                    const savedCode = localStorage.getItem('vibeproto_last_code');
                                    setTimeout(() => {
                                        forceDisplayCode(savedCode);
                                        
                                        // Double-check and force direct update if needed
                                        setTimeout(() => {
                                            if (codeDisplayElement && codeDisplayElement.textContent !== savedCode) {
                                                console.log("EMERGENCY CODE DISPLAY UPDATE FROM LOCALSTORAGE");
                                                codeDisplayElement.textContent = savedCode;
                                            }
                                        }, 300);
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