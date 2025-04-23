// Simple script for the VibeProto prototype generator

let currentSessionId = null;
let sessions = [];

// Load sessions on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadSessions();
    document.getElementById('generate').addEventListener('click', generate);
    document.getElementById('new-session').addEventListener('click', createNewSession);
    document.getElementById('copy-code').addEventListener('click', copyCode);
    document.getElementById('download-code').addEventListener('click', downloadCode);
    document.getElementById('analyze-code').addEventListener('click', analyzeCode);
    document.getElementById('enhance-prompt').addEventListener('click', enhancePrompt);
});

async function loadSessions() {
    const response = await fetch('http://localhost:5000/get_sessions');
    sessions = await response.json();
    const sessionList = document.getElementById('session-list');
    sessionList.innerHTML = ''; // Clear existing list
    sessions.forEach(session => {
        const sessionItemContainer = document.createElement('div');
        sessionItemContainer.className = 'session-item';

        const sessionNameDiv = document.createElement('div');
        sessionNameDiv.className = 'session-name';
        sessionNameDiv.textContent = session.name || `Session ${session.id}`;
        sessionNameDiv.onclick = () => loadSession(session.id); // Click name to load

        const sessionActionsDiv = document.createElement('div');
        sessionActionsDiv.className = 'session-actions';
        sessionActionsDiv.style.position = 'relative'; // Needed for absolute positioning of dropdown

        const menuTrigger = document.createElement('button');
        menuTrigger.className = 'menu-trigger action-button'; // Reuse action-button style
        menuTrigger.innerHTML = '&#8942;'; // Vertical ellipsis HTML entity
        
        const dropdownMenu = document.createElement('div');
        dropdownMenu.className = 'dropdown-menu';
        // Initially hidden, position will be handled by CSS

        const renameItem = document.createElement('div');
        renameItem.className = 'dropdown-item';
        renameItem.textContent = 'Rename';
        renameItem.onclick = (event) => {
            event.stopPropagation();
            dropdownMenu.classList.remove('visible'); // Hide menu
            startRenameSession(session.id, session.name || `Session ${session.id}`);
        };

        const deleteItem = document.createElement('div');
        deleteItem.className = 'dropdown-item';
        deleteItem.textContent = 'Delete';
        deleteItem.onclick = (event) => {
            event.stopPropagation();
            dropdownMenu.classList.remove('visible'); // Hide menu
            deleteSession(session.id);
        };

        dropdownMenu.appendChild(renameItem);
        dropdownMenu.appendChild(deleteItem);

        menuTrigger.onclick = (event) => {
            event.stopPropagation();
            // Close all other open menus first
            document.querySelectorAll('.dropdown-menu.visible').forEach(menu => {
                if (menu !== dropdownMenu) {
                    menu.classList.remove('visible');
                }
            });
            // Toggle the current menu
            dropdownMenu.classList.toggle('visible');
        };

        sessionActionsDiv.appendChild(menuTrigger);
        sessionActionsDiv.appendChild(dropdownMenu);

        sessionItemContainer.appendChild(sessionNameDiv);
        sessionItemContainer.appendChild(sessionActionsDiv);
        sessionList.appendChild(sessionItemContainer);
    });
    
    // Add a global click listener to close menus when clicking outside
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.session-actions')) {
            document.querySelectorAll('.dropdown-menu.visible').forEach(menu => {
                menu.classList.remove('visible');
            });
        }
    }, true); // Use capture phase to catch clicks reliably
}

async function createNewSession() {
    const response = await fetch('http://localhost:5000/create_session', { method: 'POST' });
    const newSession = await response.json();
    currentSessionId = newSession.id;
    await loadSessions();
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('code-output').innerHTML = '<pre>Generated code will appear here...</pre>';
}

async function loadSession(sessionId) {
    currentSessionId = sessionId;
    const response = await fetch(`http://localhost:5000/get_session/${sessionId}`);
    const session = await response.json();
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    session.messages.forEach(msg => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${msg.role}-message`;
        msgDiv.textContent = msg.content;
        chatMessages.appendChild(msgDiv);
    });
    
    // Use the helper function to display code and instructions
    displayGeneratedCodeAndInstructions(session.code, session.instructions);

    chatMessages.scrollTop = chatMessages.scrollHeight;
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

    const chatMessages = document.getElementById('chat-messages');
    const userMsg = document.createElement('div');
    userMsg.className = 'message user-message';
    userMsg.textContent = prompt;
    chatMessages.appendChild(userMsg);

    const status = document.getElementById('status');
    status.textContent = 'Generating your prototype... This may take a minute.';

    try {
        const response = await fetch('http://localhost:5000/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, type: prototypeType, session_id: currentSessionId })
        });
        const data = await response.json();

        const systemMsg = document.createElement('div');
        systemMsg.className = 'message system-message';
        systemMsg.textContent = data.explanation || 'Generated successfully!';
        chatMessages.appendChild(systemMsg);

        const codeOutput = document.getElementById('code-output');
        
        // Use the helper function to display code and instructions
        displayGeneratedCodeAndInstructions(data.code, data.instructions);

        status.textContent = data.explanation || 'Generation complete!';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
        console.error('Error:', error);
        status.textContent = 'Error generating code. Check console.';
    }

    document.getElementById('prompt').value = '';
    await loadSessions();
}

function getCombinedCode() {
    const codeOutput = document.getElementById('code-output');
    // We need to reconstruct the code from the potentially structured HTML
    let combinedCode = "";
    const preElements = codeOutput.querySelectorAll('pre');
    preElements.forEach(pre => {
        // Add language comment based on sibling comments or class
        let langComment = "";
        if (pre.previousSibling && pre.previousSibling.nodeType === Node.COMMENT_NODE) {
            langComment = `<!-- ${pre.previousSibling.textContent.trim()} -->\n`;
        } else if (pre.querySelector('code[class*="language-"]')) {
            const lang = pre.querySelector('code[class*="language-"]').className.replace("language-", "");
            if (lang === 'css') langComment = `/* ${lang.toUpperCase()} */\n`;
            else if (lang === 'javascript') langComment = `// ${lang.toUpperCase()}\n`;
            else langComment = `<!-- ${lang.toUpperCase()} -->\n`; // Default to HTML comment
        }
        
        combinedCode += langComment + pre.textContent + "\n\n";
    });
    
    // Fallback if no pre elements found (e.g., simple text node)
    if (!combinedCode.trim() && codeOutput.textContent) {
        combinedCode = codeOutput.textContent;
    }
    
    return combinedCode.trim();
}

function copyCode() {
    const code = getCombinedCode();
    navigator.clipboard.writeText(code).then(() => {
        alert('Code copied to clipboard!');
    });
}

function downloadCode() {
    const code = getCombinedCode();
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated_code.txt'; // Consider dynamic name later
    a.click();
    URL.revokeObjectURL(url); 
}

function analyzeCode() {
    const code = document.getElementById('code-output').textContent;
    alert('Analysis feature coming soon! Code length: ' + code.length + ' characters.');
}

async function enhancePrompt() {
    const promptTextarea = document.getElementById('prompt');
    const currentPrompt = promptTextarea.value.trim();
    const status = document.getElementById('status');

    if (!currentPrompt) {
        alert('Please enter a prompt first.');
        return;
    }

    status.textContent = 'Enhancing prompt...';

    try {
        const response = await fetch('http://localhost:5000/enhance_prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: currentPrompt })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to enhance prompt');
        }

        const data = await response.json();
        
        if (data.enhanced_prompt) {
            promptTextarea.value = data.enhanced_prompt;
            status.textContent = 'Prompt enhanced!';
            // Optionally add a message to the chat
            const chatMessages = document.getElementById('chat-messages');
            const enhanceMsg = document.createElement('div');
            enhanceMsg.className = 'message system-message info-message'; // Add specific class if needed
            enhanceMsg.textContent = `Prompt enhanced: ${data.enhanced_prompt}`;
            chatMessages.appendChild(enhanceMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else {
            status.textContent = 'Could not enhance prompt.';
        }

    } catch (error) {
        console.error('Error enhancing prompt:', error);
        status.textContent = `Error: ${error.message}`;
    }
}

async function deleteSession(sessionId) {
    if (!confirm(`Are you sure you want to delete session ${sessionId}?`)) {
        return; // User cancelled
    }

    try {
        const response = await fetch(`http://localhost:5000/delete_session/${sessionId}`, {
            method: 'POST',
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to delete session');
        }

        alert('Session deleted successfully.');
        
        // If the deleted session was the current one, clear the main view
        if (currentSessionId === sessionId) {
            currentSessionId = null;
            document.getElementById('chat-messages').innerHTML = '';
            document.getElementById('code-output').innerHTML = '<pre>Select or create a session.</pre>';
            document.getElementById('prompt').value = '';
            document.getElementById('status').textContent = 'Session deleted.';
        }
        
        // Reload the session list
        await loadSessions();

    } catch (error) {
        console.error('Error deleting session:', error);
        alert(`Error deleting session: ${error.message}`);
    }
}

// --- New Helper Function --- 
function displayGeneratedCodeAndInstructions(code, instructions) {
    const codeOutput = document.getElementById('code-output');
    codeOutput.innerHTML = ''; // Clear previous content

    // Check if the code is structured (web app) or a single string (script)
    if (typeof code === 'object' && code !== null && ('html' in code || 'css' in code || 'javascript' in code)) {
        // Format structured code for display
        let formattedCode = "";
        if (code.html) {
            formattedCode += `<!-- HTML -->\n<pre><code class="language-html">${escapeHtml(code.html)}</code></pre>\n\n`;
        }
        if (code.css) {
            formattedCode += `/* CSS */\n<pre><code class="language-css">${escapeHtml(code.css)}</code></pre>\n\n`;
        }
        if (code.javascript) {
            formattedCode += `// JavaScript\n<pre><code class="language-javascript">${escapeHtml(code.javascript)}</code></pre>\n`;
        }
        // Use innerHTML to render multiple pre/code blocks
        codeOutput.innerHTML = formattedCode || "<pre>Received web app data, but no code found.</pre>";
        // Apply highlighting if using a library like highlight.js
        // if (typeof hljs !== 'undefined') { hljs.highlightAllUnder(codeOutput); }
    } else if (typeof code === 'string') {
        // Display single code string (e.g., Python script)
        codeOutput.innerHTML = `<pre>${escapeHtml(code)}</pre>`;
    } else {
        // Handle unexpected code format or empty code
        codeOutput.innerHTML = '<pre>Generated code will appear here...</pre>'; // Default placeholder
    }
    
    // Append instructions if they exist
    if (instructions) {
        const instructionsDiv = document.createElement('div');
        instructionsDiv.className = 'code-instructions';
        // Simple formatting: replace markdown-like ### heading and backticks
        let formattedInstructions = instructions
            .replace(/### (.*)/g, '<h4>$1</h4>') // Replace ### heading with h4
            .replace(/`([^`]*)`/g, '<code>$1</code>'); // Replace backticks with code tags
        instructionsDiv.innerHTML = formattedInstructions;
        codeOutput.appendChild(instructionsDiv); // Append after code blocks
    }
}

// Helper function to escape HTML entities for safe display
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }

function startRenameSession(sessionId, currentName) {
    const newName = prompt(`Enter new name for session (currently "${currentName}"):`, currentName);
    
    if (newName !== null && newName.trim() !== '' && newName !== currentName) {
        // Only proceed if a non-empty, different name was entered
        confirmRenameSession(sessionId, newName.trim());
    }
}

async function confirmRenameSession(sessionId, newName) {
    try {
        const response = await fetch(`http://localhost:5000/rename_session/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_name: newName })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to rename session');
        }

        const result = await response.json();
        console.log('Rename successful:', result);
        alert('Session renamed successfully.');
        await loadSessions(); // Refresh the list

    } catch (error) {
        console.error('Error renaming session:', error);
        alert(`Error renaming session: ${error.message}`);
    }
} 