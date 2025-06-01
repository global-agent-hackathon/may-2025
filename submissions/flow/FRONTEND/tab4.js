import { generateVector } from './generateVector.js';
import { fetchAiResponse } from './fetchAiResponse.js';

export function initializeTab4() {
    console.log('Initializing Tab4...');

    // Get DOM elements
    const loadingMessage3 = document.getElementById('loading-message3');
    const vectorBtn = document.getElementById('VectorBtn');
    const generateIconForm = document.getElementById('generate-icon-form');
    const submitIcon = document.getElementById('submitIcon');

    // State management
    let isVectorTabActive = false;

    // Function to switch between tabs
    function switchTab(activeButton) {
        console.log('Switching to tab:', activeButton.id);

        // Update button states
        document.querySelectorAll('#capture-container button').forEach(btn => {
            btn.classList.remove('active');
            btn.style.backgroundColor = 'white';
            btn.style.color = 'black';
        });

        // Add active class to clicked button
        activeButton.classList.add('active');
        activeButton.style.backgroundColor = '#0a5ecb';
        activeButton.style.color = 'white';

        // Update tab state
        isVectorTabActive = activeButton.id === 'VectorBtn';

        // Reset UI elements
        const elementsToReset = [
            'successIcon',
            'loadingMessage',
            'analysisOutput',
            'generate-icon-form',
            'svgContainer',
            'showCodeButton',
            'copyCodeButton',
            'saveSvgButton',
            'svgCodeDisplay'
        ];
        elementsToReset.forEach(id => {
            document.getElementById(id).style.display = 'none';
        });
    }

    // Event listeners for tab buttons
    vectorBtn.addEventListener('click', () => {
        switchTab(vectorBtn);
        generateIconForm.style.display = 'block';
    });

    // Add event listeners to analysis buttons

    // Handle icon submission
    submitIcon.addEventListener('click', async () => {
        const fontInput2 = document.getElementById('fontInput2').value;

        if (!fontInput2) {
            alert('Please enter a design description.');
            return;
        }

        loadingMessage3.style.display = 'block';
        loadingMessage3.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #0a5ecb;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 10px auto;
                "></div>
                <p style="color: #666; margin-top: 10px;">Generating vector icon...</p>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;

        try {
            const promptText = `Generate an SVG icon code based on the following description: "${fontInput2}"`;
            const result = await fetchAiResponse(promptText);
            const svgCode = extractSvgCode(result);

            if (svgCode) {
                console.log('Extracted SVG Code:', svgCode);
                generateVector(svgCode);
                loadingMessage3.innerHTML = `
                    <div style="text-align: center; padding: 10px;">
                        <span style="
                            background-color: #d1fae5;
                            color: #059669;
                            padding: 8px 16px;
                            border-radius: 20px;
                            font-size: 14px;
                            display: inline-block;
                        ">
                            Vector icon generated successfully!
                        </span>
                    </div>`;
            } else {
                loadingMessage3.innerHTML = '<p style="color: #dc3545; text-align: center;">No SVG code found in the generated text.</p>';
            }
        } catch (error) {
            console.error('Error generating SVG:', error);
            loadingMessage3.innerHTML = '<p style="color: #dc3545; text-align: center;">An error occurred while generating the SVG.</p>';
        }
    });

    // Helper function to extract SVG code from AI response
    function extractSvgCode(result) {
        const svgMatch = result.match(/<svg[^>]*>([\s\S]*?)<\/svg>/i);
        return svgMatch?.[0] || null;
    }

    // Initialize with no tab selected
    document.querySelectorAll('#capture-container button').forEach(btn => {
        btn.classList.remove('active');
        btn.style.backgroundColor = 'white';
        btn.style.color = 'black';
    });

    // Hide all content initially
    generateIconForm.style.display = 'none';
    loadingMessage3.style.display = 'none';

    console.log('Tab4 initialization completed with no tab selected');
}

