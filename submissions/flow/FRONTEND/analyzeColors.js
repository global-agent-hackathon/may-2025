import { fetchColorNames } from './fetchColorNames.js';

// ✅ Updated to fetch from your Python backend
async function fetchAiResponse(prompt) {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/ai-response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error fetching AI response from server:', error);
        throw new Error('Failed to fetch AI response.');
    }
}

// 🧠 Handles response rendering
async function handleAiRequest(prompt) {
    const resultCard = document.getElementById('resultCard');
    const aiResponseText = document.getElementById('aiResponseText');
    const loadingMessage = document.getElementById('loading-message2');

    try {
        // Show loading message and hide result card
        loadingMessage.style.display = 'block';
        resultCard.style.display = 'none';
        aiResponseText.textContent = ''; // Clear previous response

        const result = await fetchAiResponse(prompt);

        // Format the response with proper markdown
        const formattedResult = result
            .replace(/### (.*?)(?:\n|$)/g, '<h3>$1</h3>')  // Headers
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>')  // Italic
            .replace(/\n- (.*?)(?:\n|$)/g, '<li>$1</li>')  // List items
            .replace(/\n/g, '<br>');  // Line breaks

        // Update the response text with formatted HTML
        aiResponseText.innerHTML = formattedResult;
        resultCard.style.display = 'block';
    } catch (error) {
        console.error('Error running AI session:', error);
        aiResponseText.textContent = 'An error occurred. Please try again.';
        resultCard.style.display = 'block';
    } finally {
        loadingMessage.style.display = 'none';
    }
}

// 🎨 Triggered by a color analysis button
export async function analyzeColors(buttonId, promptSuffix) {
    const colorBoxes = document.querySelectorAll('.color-box');
    const hexCodes = Array.from(colorBoxes).map(box => {
        const hexCode = box.getAttribute('data-hex');
        return hexCode.startsWith('#') ? hexCode.slice(1) : hexCode;
    });

    if (hexCodes.length === 0) {
        alert('No colors in the palette to analyze.');
        return;
    }

    console.log('Hex codes:', hexCodes.join(', '));

    try {
        const colorNames = await fetchColorNames(hexCodes);
        const colorsForAnalysis = colorNames.join(', ');
        const prompt = `${promptSuffix}: ${colorsForAnalysis}.`;
        await handleAiRequest(prompt);
    } catch (error) {
        alert(error.message);
    }
}
