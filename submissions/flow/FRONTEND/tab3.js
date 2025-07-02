import { fetchAiResponse } from './fetchAiResponse.js';
import { renderFontCards } from './renderFontCards.js';

export function initializeTab3() {
    console.log('Initializing Tab3...');

    // Get DOM elements
    const fontBtn = document.getElementById('fontBtn');
    const generateFontForm = document.getElementById('generate-font-form');
    const submitFontBtn = document.getElementById('submitFont');
    const loadingMessage = document.getElementById('loading-message4');
    const analysisOutput = document.getElementById('analysisOutput1');
    const fontCardsContainer = document.createElement('div');
    fontCardsContainer.style.display = 'none';
    document.getElementById('tab3').appendChild(fontCardsContainer);

    // State management
    let shouldCancelAnalysis = false;
    let isGenerateTabActive = false;

    // Function to switch between font tabs
    function switchFontTab(activeButton) {
        console.log('Switching to tab:', activeButton.id);

        // Cancel any ongoing analysis
        shouldCancelAnalysis = true;
        if (window.currentFontAnalysisProcess) {
            window.currentFontAnalysisProcess = null;
        }

        // Update button states
        document.querySelectorAll('#capture-container button').forEach(btn => {
            btn.classList.remove('active');
            btn.style.backgroundColor = 'white';
            btn.style.color = 'black';
        });

        activeButton.classList.add('active');
        activeButton.style.backgroundColor = '#0a5ecb';
        activeButton.style.color = 'white';

        // Update tab state
        isGenerateTabActive = activeButton.id === 'fontBtn';

        // Reset UI elements
        const elementsToReset = [
            generateFontForm,
            fontCardsContainer,
            loadingMessage
        ];
        elementsToReset.forEach(element => {
            element.style.display = 'none';
        });

        fontCardsContainer.innerHTML = '';
        loadingMessage.textContent = 'Loading...';

        // Handle analysis output
        if (isGenerateTabActive) {
            analysisOutput.style.display = 'none';
            analysisOutput.textContent = '';
            if (analysisOutput.parentNode) {
                analysisOutput.parentNode.removeChild(analysisOutput);
            }
        } else if (!document.getElementById('analysisOutput1')) {
            document.getElementById('tab3').appendChild(analysisOutput);
        }
    }

    // Event listeners
    fontBtn.addEventListener('click', () => {
        console.log('Font generate button clicked');
        switchFontTab(fontBtn);
        generateFontForm.style.display = 'block';
    });

    submitFontBtn.addEventListener('click', async () => {
        const fontInput = document.getElementById('fontInput').value;

        if (!fontInput) {
            alert('Please enter a design description.');
            return;
        }

        loadingMessage.style.display = 'block';
        fontCardsContainer.style.display = 'none';
        fontCardsContainer.innerHTML = '';

        try {
            const promptText = `Based on this design description: "${fontInput}", suggest 6 Google Fonts that would be perfect for this project. For each font, provide:
1. The exact font name
2. The Google Fonts URL in this format: https://fonts.googleapis.com/css2?family=FontName:wght@400&display=swap

Format your response exactly like this example:
Roboto
https://fonts.googleapis.com/css2?family=Roboto:wght@400&display=swap
Open Sans
https://fonts.googleapis.com/css2?family=Open+Sans:wght@400&display=swap

Make sure to use the exact font names and URLs as shown in the example.`;

            const result = await fetchAiResponse(promptText);

            // Process the response to extract font names and URLs
            const lines = result.split('\n').map(line => line.trim()).filter(line => line);
            const fontLinks = [];

            for (let i = 0; i < lines.length; i += 2) {
                if (i + 1 < lines.length && lines[i + 1].includes('fonts.googleapis.com')) {
                    fontLinks.push(lines[i + 1]);
                }
            }

            if (fontLinks.length > 0) {
                await renderFontCards(fontLinks, fontCardsContainer);
                fontCardsContainer.style.display = 'flex';
                fontCardsContainer.style.flexWrap = 'wrap';
                fontCardsContainer.style.gap = '10px';
                fontCardsContainer.style.justifyContent = 'center';
            } else {
                if (document.getElementById('analysisOutput1')) {
                    analysisOutput.textContent = 'No suitable fonts found. Please try again.';
                    analysisOutput.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Error in font generation process:', error);
            if (document.getElementById('analysisOutput1')) {
                analysisOutput.textContent = 'An error occurred. Please try again.';
                analysisOutput.style.display = 'block';
            }
        } finally {
            loadingMessage.style.display = 'none';
        }
    });

    // Initialize with no tab selected
    document.querySelectorAll('#capture-container button').forEach(btn => {
        btn.classList.remove('active');
        btn.style.backgroundColor = 'white';
        btn.style.color = 'black';
    });

    // Hide all content initially
    generateFontForm.style.display = 'none';
    fontCardsContainer.style.display = 'none';
    loadingMessage.style.display = 'none';
    analysisOutput.style.display = 'none';

    console.log('Tab3 initialization completed with no tab selected');
}
