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

// Load sessions on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadSessions();
    document.getElementById('generate').addEventListener('click', generate);
    document.getElementById('enhance-prompt').addEventListener('click', enhancePrompt);
    document.getElementById('new-session').addEventListener('click', createNewSession);
    document.getElementById('copy-code').addEventListener('click', copyCode);
    document.getElementById('download-code').addEventListener('click', downloadCode);
    document.getElementById('analyze-code').addEventListener('click', analyzeCode);
    
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
        } else {
            alert('Failed to rename session');
        }
    } catch (error) {
        console.error('Error renaming session:', error);
        alert('Error renaming session: ' + error.message);
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
                document.getElementById('code-output').innerHTML = '<pre>Generated code will appear here...</pre>';
            }
            
            // Reload the sessions list
            await loadSessions();
        } else {
            alert('Failed to delete session');
        }
    } catch (error) {
        console.error('Error deleting session:', error);
        alert('Error deleting session: ' + error.message);
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
    document.getElementById('code-output').innerHTML = '<pre>Generated code will appear here...</pre>';
}

async function loadSession(sessionId) {
    currentSessionId = sessionId;
    const response = await fetch(`http://localhost:5000/get_session/${sessionId}?user_id=${userId}`, {
        method: 'GET',
        headers: {
            'Access-Control-Allow-Origin': '*'
        },
        mode: 'cors'
    });
    const session = await response.json();
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    
    if (session.messages) {
        session.messages.forEach(msg => {
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${msg.role}-message`;
            msgDiv.textContent = msg.content;
            chatMessages.appendChild(msgDiv);
        });
    }
    
    if (session.code) {
        console.log("Loading code from session:", session.code);
        
        // Escape HTML to prevent issues with code that contains HTML
        const escapedCode = session.code
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
            
        document.getElementById('code-output').innerHTML = `<pre>${escapedCode}</pre>`;
    } else {
        document.getElementById('code-output').innerHTML = '<pre>Generated code will appear here...</pre>';
    }
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Enhance prompt function
async function enhancePrompt() {
    const prompt = document.getElementById('prompt').value.trim();
    if (!prompt) {
        alert('Please enter a prompt to enhance.');
        return;
    }

    // Show loading state
    const enhanceButton = document.getElementById('enhance-prompt');
    const originalText = enhanceButton.textContent;
    enhanceButton.textContent = 'Enhancing...';
    enhanceButton.disabled = true;

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

    try {
        if (remoteMode) {
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

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const result = await response.json();
            
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

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const result = await response.json();
            console.log('Enhanced prompt result:', result);

            if (!result.enhanced_prompt) {
                throw new Error('No enhanced prompt received from server');
            }

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
            
            // Reset button state for immediate mode
            enhanceButton.textContent = originalText;
            enhanceButton.disabled = false;
        }
    } catch (error) {
        console.error('Error enhancing prompt:', error);
        alert(`Error enhancing prompt: ${error.message}`);
        
        // Reset button state
        enhanceButton.textContent = originalText;
        enhanceButton.disabled = false;
    }
}

async function generate() {
    if (!currentSessionId) {
        await createNewSession();
    }

    const prompt = document.getElementById('prompt').value.trim();
    const prototypeType = document.getElementById('prototype-type').value;
    if (!prompt) {
        alert('Please enter a prompt.');
        return;
    }

    // Show loading state
    const generateButton = document.getElementById('generate');
    const originalText = generateButton.textContent;
    generateButton.textContent = 'Generating...';
    generateButton.disabled = true;

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
                alert(result.error);
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
                alert(result.error);
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

            // Display the generated code
            if (result.code) {
                // Escape HTML to prevent issues with code that contains HTML
                const escapedCode = result.code
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
                document.getElementById('code-output').innerHTML = `<pre>${escapedCode}</pre>`;
                
                // Also log the code to console for debugging
                console.log("Generated code:", result.code);
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
        alert('Error generating code: ' + error.message);
        
        // Reset button state
        generateButton.textContent = originalText;
        generateButton.disabled = false;
    }
}

function copyCode() {
    const code = document.getElementById('code-output').textContent;
    navigator.clipboard.writeText(code).then(() => alert('Code copied to clipboard!'));
}

function downloadCode() {
    const code = document.getElementById('code-output').textContent;
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated_code.txt';
    a.click();
    URL.revokeObjectURL(url);
}

function analyzeCode() {
    alert('Code analysis feature coming soon!');
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
            alert('API keys saved successfully!');
            loadApiKeys();  // Refresh the status
            modal.style.display = "none";
            location.reload();  // Reload the page to reinitialize with new keys
        } else {
            const error = await response.json();
            alert('Failed to save API keys: ' + error.error);
        }
    } catch (error) {
        console.error('Error saving API keys:', error);
        alert('Failed to save API keys. Please try again.');
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
    }
}

function handleRemoteEnhanceResult(taskStatus) {
    const enhanceButton = document.getElementById('enhance-prompt');
    enhanceButton.textContent = 'Enhance Prompt';
    enhanceButton.disabled = false;
    
    if (taskStatus.error) {
        alert(`Error enhancing prompt: ${taskStatus.error}`);
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
        alert(`Error generating code: ${taskStatus.error}`);
        return;
    }
    
    // Get the result data
    const result = taskStatus.result;
    
    // Display the generated code
    if (result && result.code) {
        // Escape HTML to prevent issues with code that contains HTML
        const escapedCode = result.code
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
        document.getElementById('code-output').innerHTML = `<pre>${escapedCode}</pre>`;
        
        // Also log the code to console for debugging
        console.log("Generated code:", result.code);
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