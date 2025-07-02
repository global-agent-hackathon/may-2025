
// Parse flashcards from markdown content
function parseFlashcards(content) {
    console.log('Parsing flashcards from content:', content);
    const cards = [];

    // Find all card sections using a more flexible pattern
    const cardMatches = content.match(/Card \d+:(.*?)(?=Card \d+:|$)/gs);

    if (!cardMatches) {
        console.log('No card matches found');
        return cards;
    }

    cardMatches.forEach((section, index) => {
        // Extract front and back content
        const frontMatch = section.match(/Front:(.*?)(?=Back:|$)/s);
        const backMatch = section.match(/Back:(.*?)(?=Card \d+:|$)/s);

        if (!frontMatch || !backMatch) {
            console.log('Skipping invalid card format:', section);
            return;
        }

        const front = frontMatch[1].trim();
        const backContent = backMatch[1].trim();

        // Process back content
        const backSections = {
            definition: '',
            keyPoints: [],
            examples: [],
            context: ''
        };

        // Parse back sections with more flexible matching
        const definitionMatch = backContent.match(/### Definition\s*([\s\S]*?)(?=### |$)/i);
        if (definitionMatch) {
            backSections.definition = definitionMatch[1].trim();
        }

        const keyPointsMatch = backContent.match(/### Key Points\s*([\s\S]*?)(?=### |$)/i);
        if (keyPointsMatch) {
            backSections.keyPoints = keyPointsMatch[1].split('\n')
                .filter(line => line.trim().startsWith('-'))
                .map(line => line.trim().substring(1).trim());
        }

        const examplesMatch = backContent.match(/### Examples\s*([\s\S]*?)(?=### |$)/i);
        if (examplesMatch) {
            backSections.examples = examplesMatch[1].split('\n')
                .filter(line => line.trim().startsWith('-'))
                .map(line => line.trim().substring(1).trim());
        }

        const contextMatch = backContent.match(/### Additional Context\s*([\s\S]*?)(?=### |$)/i);
        if (contextMatch) {
            backSections.context = contextMatch[1].trim();
        }

        // Format the back content
        const formattedBack = `
            <div class="flashcard-sections">
                ${backSections.definition ? `
                    <div class="section definition">
                        <h3>Definition</h3>
                        <div class="content">${backSections.definition}</div>
                    </div>
                ` : ''}
                
                ${backSections.keyPoints.length > 0 ? `
                    <div class="section key-points">
                        <h3>Key Points</h3>
                        <ul>
                            ${backSections.keyPoints.map(point => `<li>${point}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${backSections.examples.length > 0 ? `
                    <div class="section examples">
                        <h3>Examples</h3>
                        <ul>
                            ${backSections.examples.map(example => `<li>${example}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${backSections.context ? `
                    <div class="section context">
                        <h3>Additional Context</h3>
                        <div class="content">${backSections.context}</div>
                    </div>
                ` : ''}
            </div>
        `;

        cards.push({
            number: index + 1,
            front: front,
            back: formattedBack
        });
    });

    console.log('Parsed cards:', cards);
    return cards;
}

export function initializeTab7() {
    console.log('Initializing Tab7...');

    // Get DOM elements
    const flashcardBtn = document.getElementById('flashcardBtn');
    const generateFlashcardForm = document.getElementById('generate-flashcard-form');
    const submitFlashcard = document.getElementById('submitFlashcard');
    const loadingMessage = document.getElementById('loading-message7');
    const flashcardOutput = document.getElementById('flashcardOutput');
    const flashcardFront = document.getElementById('flashcardFront');
    const flashcardBack = document.getElementById('flashcardBack');
    const flashcardInner = document.getElementById('flashcardInner');
    const flashcardCounter = document.getElementById('flashcardCounter');
    const prevFlashcardBtn = document.getElementById('prevFlashcardBtn');
    const nextFlashcardBtn = document.getElementById('nextFlashcardBtn');
    const copyFlashcardBtn = document.getElementById('copyFlashcardBtn');

    let currentCards = [];
    let currentCardIndex = 0;
    let isFlipped = false;

    // Show flashcard generation form when button is clicked
    flashcardBtn.addEventListener('click', () => {
        document.querySelectorAll('#capture-container button').forEach(btn => {
            btn.classList.remove('active');
            btn.style.backgroundColor = 'white';
            btn.style.color = 'black';
        });
        flashcardBtn.classList.add('active');
        flashcardBtn.style.backgroundColor = '#0a5ecb';
        flashcardBtn.style.color = 'white';
        generateFlashcardForm.style.display = 'block';
        flashcardOutput.style.display = 'none';
    });

    // Handle flashcard generation
    submitFlashcard.addEventListener('click', async () => {
        const urlInput = document.getElementById('urlInput').value;

        if (!urlInput) {
            alert('Please enter a URL.');
            return;
        }

        // Validate URL format
        try {
            new URL(urlInput);
        } catch (e) {
            alert('Please enter a valid URL.');
            return;
        }

        loadingMessage.style.display = 'block';
        flashcardOutput.style.display = 'none';

        try {
            const response = await fetch('http://localhost:5000/api/generate-flashcards', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: urlInput })
            });

            const data = await response.json();
            console.log('Received response:', data);

            if (data.error) {
                throw new Error(data.error);
            }

            if (!data.flashcards) {
                throw new Error('No flashcards were generated');
            }

            // Parse flashcards from the response
            currentCards = parseFlashcards(data.flashcards);
            console.log('Current cards after parsing:', currentCards);

            if (currentCards.length === 0) {
                throw new Error('No flashcards were generated');
            }

            currentCardIndex = 0;
            isFlipped = false;

            // Update UI
            updateFlashcardDisplay();
            flashcardOutput.style.display = 'block';

            // Add styles for better flashcard display
            const style = document.createElement('style');
            style.textContent = `
                #flashcardOutput {
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                }
                
                #flashcardInner {
                    min-height: 400px;
                    width: 100%;
                    position: relative;
                    transform-style: preserve-3d;
                    transition: transform 0.8s;
                }
                
                #flashcardFront, #flashcardBack {
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    backface-visibility: hidden;
                    border-radius: 16px;
                    padding: 30px;
                    box-sizing: border-box;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                }
                
                #flashcardFront {
                    background: linear-gradient(135deg, #f0f4ff 0%, #e6eeff 100%);
                    border: 2px solid #0a5ecb;
                }
                
                #flashcardBack {
                    background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
                    border: 2px solid #0a5ecb;
                    transform: rotateY(180deg);
                }
                
                .flashcard-content {
                    flex: 1;
                    overflow-y: auto;
                    padding-right: 10px;
                }
                
                .flashcard-content::-webkit-scrollbar {
                    width: 8px;
                }
                
                .flashcard-content::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 4px;
                }
                
                .flashcard-content::-webkit-scrollbar-thumb {
                    background: #0a5ecb;
                    border-radius: 4px;
                }
                
                .flashcard-content::-webkit-scrollbar-thumb:hover {
                    background: #0848a3;
                }
                
                .flashcard-sections {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                
                .section {
                    background: rgba(255, 255, 255, 0.8);
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }
                
                .section h3 {
                    color: #0a5ecb;
                    margin-top: 0;
                    margin-bottom: 10px;
                    font-size: 1.2em;
                }
                
                .section ul {
                    margin: 0;
                    padding-left: 20px;
                }
                
                .section li {
                    margin: 5px 0;
                }
                
                .section .content {
                    line-height: 1.6;
                }
                
                #flashcardCounter {
                    text-align: center;
                    margin: 15px 0;
                    color: #666;
                    font-size: 14px;
                    font-weight: 500;
                }
                
                #flashcardOutput button {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 20px;
                    background: #f0f4ff;
                    color: #0a5ecb;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s ease;
                    font-weight: 500;
                }
                
                #flashcardOutput button:hover {
                    background: #0a5ecb;
                    color: white;
                }
                
                #flashcardOutput button:disabled {
                    background: #f0f4ff;
                    color: #a0a0a0;
                    cursor: not-allowed;
                }

                .export-pdf-btn {
                    margin-bottom: 15px;
                    background: #0a5ecb !important;
                    color: white !important;
                }

                .export-pdf-btn:hover {
                    background: #0848a3 !important;
                }
            `;
            document.head.appendChild(style);

            // Add PDF export button
            const exportBtn = document.createElement('button');
            exportBtn.className = 'export-pdf-btn';
            exportBtn.innerHTML = `
                <svg class="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 13V4M12 13l-4-4m4 4 4-4M3 20v-1a3 3 0 0 1 3-3h12a3 3 0 0 1 3 3v1"/>
                </svg>
                Export All Cards as PDF
            `;
            exportBtn.onclick = exportToPDF;
            flashcardOutput.insertBefore(exportBtn, flashcardOutput.firstChild);
        } catch (error) {
            console.error('Error generating flashcards:', error);
            flashcardFront.innerHTML = `<div class="error-message">${error.message}</div>`;
            flashcardBack.innerHTML = '';
            flashcardOutput.style.display = 'block';
        } finally {
            loadingMessage.style.display = 'none';
        }
    });

    // Handle flashcard navigation
    function updateFlashcardDisplay() {
        console.log('Updating flashcard display. Current index:', currentCardIndex);
        console.log('Current cards:', currentCards);

        if (currentCards.length === 0) {
            console.log('No cards to display');
            return;
        }

        const card = currentCards[currentCardIndex];
        console.log('Current card:', card);

        // Update front content
        flashcardFront.innerHTML = `
            <div class="flashcard-content">
                <h2>${card.front}</h2>
            </div>
        `;

        // Update back content
        flashcardBack.innerHTML = `
            <div class="flashcard-content">
                ${card.back}
            </div>
        `;

        // Update counter
        flashcardCounter.textContent = `Card ${currentCardIndex + 1} of ${currentCards.length}`;

        // Reset flip state
        isFlipped = false;
        flashcardInner.style.transform = 'rotateY(0deg)';

        // Update button states
        prevFlashcardBtn.disabled = currentCardIndex === 0;
        nextFlashcardBtn.disabled = currentCardIndex === currentCards.length - 1;

        // Add visual feedback for disabled state
        prevFlashcardBtn.style.opacity = prevFlashcardBtn.disabled ? '0.5' : '1';
        nextFlashcardBtn.style.opacity = nextFlashcardBtn.disabled ? '0.5' : '1';
    }

    // Handle previous button click
    prevFlashcardBtn.addEventListener('click', () => {
        if (currentCardIndex > 0) {
            currentCardIndex--;
            updateFlashcardDisplay();
        }
    });

    // Handle next button click
    nextFlashcardBtn.addEventListener('click', () => {
        if (currentCardIndex < currentCards.length - 1) {
            currentCardIndex++;
            updateFlashcardDisplay();
        }
    });

    // Handle flashcard click to flip
    flashcardInner.addEventListener('click', () => {
        isFlipped = !isFlipped;
        flashcardInner.style.transform = isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)';
    });

    // Handle copy button click
    copyFlashcardBtn.addEventListener('click', async () => {
        try {
            const currentCard = currentCards[currentCardIndex];
            const textToCopy = `${currentCard.front}\n\n${currentCard.back}`;
            await navigator.clipboard.writeText(textToCopy);

            // Show feedback
            const originalText = copyFlashcardBtn.innerHTML;
            copyFlashcardBtn.innerHTML = `
                <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 24 24">
                    <path fill-rule="evenodd" d="M2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10S2 17.523 2 12Zm13.707-1.293a1 1 0 0 0-1.414-1.414L11 12.586l-1.293-1.293a1 1 0 0 0-1.414 1.414l2 2a1 1 0 0 0 1.414 0l4-4Z" clip-rule="evenodd"/>
                </svg>
                Copied!
            `;

            // Reset button after 2 seconds
            setTimeout(() => {
                copyFlashcardBtn.innerHTML = originalText;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy text to clipboard');
        }
    });

    // Add PDF export function
    async function exportToPDF() {
        try {
            // Create a temporary container for all cards
            const container = document.createElement('div');
            container.style.padding = '20px';
            container.style.backgroundColor = 'white';

            // Add each card to the container
            currentCards.forEach((card, index) => {
                const cardDiv = document.createElement('div');
                cardDiv.style.marginBottom = '30px';
                cardDiv.style.pageBreakAfter = 'always';
                cardDiv.innerHTML = `
                    <div style="border: 2px solid #0a5ecb; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
                        <h2 style="color: #0a5ecb; margin-bottom: 15px;">Card ${index + 1}</h2>
                        <div style="margin-bottom: 20px;">
                            <h3 style="color: #0a5ecb;">Front:</h3>
                            <p>${card.front}</p>
                        </div>
                        <div>
                            <h3 style="color: #0a5ecb;">Back:</h3>
                            ${card.back}
                        </div>
                    </div>
                `;
                container.appendChild(cardDiv);
            });

            // Create a new window for printing
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Flashcards</title>
                        <style>
                            body { font-family: Arial, sans-serif; }
                            @media print {
                                @page { margin: 1cm; }
                            }
                        </style>
                    </head>
                    <body>
                        ${container.innerHTML}
                    </body>
                </html>
            `);
            printWindow.document.close();

            // Wait for content to load
            printWindow.onload = function () {
                printWindow.print();
                printWindow.close();
            };
        } catch (error) {
            console.error('Error exporting to PDF:', error);
            alert('Failed to export flashcards. Please try again.');
        }
    }

    // Add function to get current tab URL
    async function getCurrentTabUrl() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            return tab.url;
        } catch (error) {
            console.error('Error getting current tab URL:', error);
            return null;
        }
    }

    // Add URL extraction button
    const urlInput = document.getElementById('urlInput');
    const urlInputContainer = urlInput.parentElement;

    // Update the input field container styling
    urlInputContainer.style.cssText = `
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 15px;
        padding: 4px 4px 4px 16px;
        background: #ffffff;
        border-radius: 24px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    `;

    urlInputContainer.addEventListener('mouseover', () => {
        urlInputContainer.style.borderColor = '#0a5ecb';
        urlInputContainer.style.boxShadow = '0 4px 12px rgba(10, 94, 203, 0.12)';
    });

    urlInputContainer.addEventListener('mouseout', () => {
        urlInputContainer.style.borderColor = '#e9ecef';
        urlInputContainer.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.04)';
    });

    // Update input field styling
    urlInput.style.cssText = `
        flex: 1;
        padding: 12px 4px;
        border: none;
        background: transparent;
        color: #1a1a1a;
        font-size: 15px;
        outline: none;
        font-family: 'Arial', sans-serif;
        letter-spacing: 0.2px;
    `;

    urlInput.placeholder = 'Enter URL to generate flashcards...';

    // Create and style the URL extraction button
    const extractUrlBtn = document.createElement('button');
    extractUrlBtn.innerHTML = `
        <svg class="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 10.5V6.75a4.5 4.5 0 1 1 9 0v3.75M3.75 21.75h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H3.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"/>
        </svg>
        <span>Current URL</span>
    `;
    extractUrlBtn.title = 'Use current tab URL';
    extractUrlBtn.style.cssText = `
        padding: 8px 16px;
        border: none;
        border-radius: 16px;
        background: #f0f4ff;
        color: #0a5ecb;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 13px;
        height: 32px;
        box-shadow: 0 2px 8px rgba(10, 94, 203, 0.1);
    `;

    // Create and style the generate button
    const generateBtn = document.createElement('button');
    generateBtn.innerHTML = `
        <svg class="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2m-6 9 2 2 4-4"/>
        </svg>
        <span>Generate</span>
    `;
    generateBtn.title = 'Generate Flashcards';
    generateBtn.style.cssText = `
        padding: 8px 16px;
        border: none;
        border-radius: 16px;
        background: #0a5ecb;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 13px;
        height: 32px;
        box-shadow: 0 2px 8px rgba(10, 94, 203, 0.2);
    `;

    // Create a container for the buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = `
        display: flex;
        gap: 8px;
        align-items: center;
    `;

    // Add buttons to the container
    buttonContainer.appendChild(extractUrlBtn);
    buttonContainer.appendChild(generateBtn);

    // Function to disable buttons
    function disableButtons() {
        extractUrlBtn.disabled = true;
        generateBtn.disabled = true;
        extractUrlBtn.style.opacity = '0.5';
        generateBtn.style.opacity = '0.5';
        extractUrlBtn.style.cursor = 'not-allowed';
        generateBtn.style.cursor = 'not-allowed';
    }

    // Function to enable buttons
    function enableButtons() {
        extractUrlBtn.disabled = false;
        generateBtn.disabled = false;
        extractUrlBtn.style.opacity = '1';
        generateBtn.style.opacity = '1';
        extractUrlBtn.style.cursor = 'pointer';
        generateBtn.style.cursor = 'pointer';
    }

    // Add click handler for the extract URL button
    extractUrlBtn.addEventListener('click', async () => {
        if (extractUrlBtn.disabled) {
            return;
        }

        disableButtons();
        try {
            const url = await getCurrentTabUrl();
            if (url) {
                urlInput.value = url;
                // Automatically trigger flashcard generation
                submitFlashcard.click();
            } else {
                alert('Could not get the current tab URL. Please make sure you have the necessary permissions.');
                enableButtons();
            }
        } catch (error) {
            console.error('Error getting URL:', error);
            alert('Error getting current URL. Please try again.');
            enableButtons();
        }
    });

    // Add click handler for the generate button
    generateBtn.addEventListener('click', () => {
        if (generateBtn.disabled) {
            return;
        }

        disableButtons();
        try {
            submitFlashcard.click();
        } catch (error) {
            console.error('Error generating flashcards:', error);
            enableButtons();
        }
    });

    // Add event listener for when flashcard generation is complete
    loadingMessage.addEventListener('transitionend', () => {
        if (loadingMessage.style.display === 'none') {
            enableButtons();
        }
    });

    // Insert the button container after the URL input
    urlInputContainer.appendChild(buttonContainer);

    // Remove the old submit button
    submitFlashcard.remove();

    // Initialize with no form visible
    generateFlashcardForm.style.display = 'none';
    flashcardOutput.style.display = 'none';
    loadingMessage.style.display = 'none';
}
