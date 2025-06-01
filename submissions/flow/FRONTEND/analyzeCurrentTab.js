import { convertMarkdownToHtml } from './MarkdownToHTML.js';

export async function analyzeCurrentTab(prompt) {
    const loadingMessage = document.getElementById('loadingMessage');
    const outputContainer = document.getElementById('analysisOutput');

    try {
        // Step 1: Show loading message
        loadingMessage.style.display = 'block';
        outputContainer.style.display = 'none';

        // Step 2: Call the analyze-images endpoint
        const response = await fetch('http://localhost:5000/api/analyze-images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt })
        });

        const result = await response.json();

        // Step 3: Display the Result
        loadingMessage.style.display = 'none';
        outputContainer.style.display = 'block';

        if (result.status === 'success') {
            outputContainer.innerHTML = convertMarkdownToHtml(result.analysis);
        } else {
            outputContainer.innerText = result.message || 'No meaningful result found. Please try again.';
        }
    } catch (error) {
        console.error('Error analyzing current tab:', error);
        loadingMessage.style.display = 'none';
        outputContainer.innerText = 'Error analyzing tab. Make sure Chrome is running with remote debugging enabled.';
    }
}
