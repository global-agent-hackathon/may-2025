document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const enhanceButton = document.getElementById('enhance-button');
    const sendButton = document.getElementById('send-button'); // Assuming this is your generate button
    const statusDiv = document.getElementById('status'); // Optional: Div to show messages

    // --- Enhance Button Logic --- 
    if (enhanceButton && promptInput) {
        enhanceButton.addEventListener('click', async () => {
            const basicPrompt = promptInput.value;
            if (!basicPrompt.trim()) {
                alert('Please enter a basic prompt first.');
                return;
            }

            // Indicate processing (optional)
            if (statusDiv) statusDiv.textContent = 'Enhancing prompt...';
            enhanceButton.disabled = true;
            if (sendButton) sendButton.disabled = true;

            try {
                const response = await fetch('/api/enhance', { // Assumes API is relative
                    method: 'POST', 
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt: basicPrompt }),
                });

                if (!response.ok) {
                    // Try to get error message from backend
                    let errorMsg = `HTTP error! status: ${response.status}`;
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.message || errorMsg;
                    } catch (jsonError) {
                        // Backend didn't send JSON error
                    }
                    throw new Error(errorMsg);
                }

                const data = await response.json();
                promptInput.value = data.enhancedPrompt; // Update the input field
                if (statusDiv) statusDiv.textContent = 'Prompt enhanced!'; // Clear status

            } catch (error) {
                console.error('Error enhancing prompt:', error);
                if (statusDiv) statusDiv.textContent = `Error: ${error.message}`;
                alert(`Failed to enhance prompt: ${error.message}`);
            } finally {
                // Re-enable buttons
                enhanceButton.disabled = false;
                if (sendButton) sendButton.disabled = false;
                // Optional: clear status after a delay
                // setTimeout(() => { if (statusDiv) statusDiv.textContent = ''; }, 3000);
            }
        });
    } else {
        console.error('Could not find prompt input or enhance button elements.');
    }

    // --- Existing Send/Generate Button Logic --- 
    // Make sure your existing logic for the sendButton is also inside this 
    // DOMContentLoaded listener or appropriately placed.
    // For example:
    if (sendButton && promptInput) {
        sendButton.addEventListener('click', () => {
            const finalPrompt = promptInput.value;
            console.log('Sending prompt for generation:', finalPrompt);
            // --- Your existing code to call the generation backend --- 
            // e.g., another fetch call to your generation endpoint
        });
    } else {
         console.error('Could not find prompt input or send button elements.');
    }

    // Add a placeholder for the status div if it doesn't exist
    if (!statusDiv) {
        console.warn('Status display element (#status) not found. Messages will appear in console/alerts.');
    }
}); 