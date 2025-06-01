import { analyzeImageWithAgno } from './imageToAgno.js';

// Function to create a font card
function createFontCard(fontData) {
    const card = document.createElement('div');
    card.className = 'font-analysis-card';
    card.style.cssText = `
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin: 10px;
        width: 300px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    `;

    // Add hover effect
    card.addEventListener('mouseover', () => {
        card.style.border = '2px solid #0a5ecb';
        card.style.transform = 'translateY(-2px)';
        card.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
    });

    card.addEventListener('mouseout', () => {
        card.style.border = '1px solid #e0e0e0';
        card.style.transform = 'translateY(0)';
        card.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    });

    // Create content structure
    const content = `
        <h3 style="color: #0a5ecb; margin: 0 0 10px 0; font-size: 18px;">${fontData.font}</h3>
        <p style="margin: 5px 0; color: #666;"><strong>Location:</strong> ${fontData.location}</p>
        <p style="margin: 5px 0; color: #666;"><strong>Characteristics:</strong> ${fontData.characteristics}</p>
        <p style="margin: 5px 0; color: #666;"><strong>Confidence:</strong> <span style="color: ${fontData.confidence === 'High' ? '#28a745' : fontData.confidence === 'Medium' ? '#ffc107' : '#dc3545'}">${fontData.confidence}</span></p>
        ${fontData.alternatives ? `<p style="margin: 5px 0; color: #666;"><strong>Alternatives:</strong> ${fontData.alternatives}</p>` : ''}
    `;

    card.innerHTML = content;

    // Add Download button
    const downloadBtn = document.createElement('button');
    downloadBtn.textContent = 'Download';
    downloadBtn.style.cssText = `
        display: block;
        width: 100%;
        margin: 10px auto 0 auto;
        padding: 8px 0;
        background: #0a5ecb;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 15px;
        cursor: pointer;
        transition: background 0.2s;
    `;
    downloadBtn.addEventListener('mouseover', () => {
        downloadBtn.style.background = '#073a8c';
    });
    downloadBtn.addEventListener('mouseout', () => {
        downloadBtn.style.background = '#0a5ecb';
    });
    downloadBtn.onclick = async () => {
        downloadBtn.disabled = true;
        downloadBtn.textContent = 'Downloading...';
        // Prepare payload
        const urlFontName = fontName.replace(/\s+/g, '+');
        const payload = {
            prompt: `Go to \"https://fonts.google.com/specimen/${urlFontName}\" and click on 'Get Font' Button and then click on 'Download all' Button.`
        };
        try {
            const response = await fetch('http://127.0.0.1:5000/api/browser/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                downloadBtn.textContent = 'Download Started!';
            } else {
                downloadBtn.textContent = 'Failed!';
            }
        } catch (e) {
            downloadBtn.textContent = 'Error!';
        }
        setTimeout(() => {
            downloadBtn.textContent = 'Download';
            downloadBtn.disabled = false;
        }, 2000);
    };
    card.appendChild(downloadBtn);

    return card;
}

// Function to parse the analysis result into structured data
function parseAnalysisResult(result) {
    console.log('Raw analysis result:', result); // Debug log

    // Split by double newlines and filter out empty entries
    const fontEntries = result.split(/\n\n+/).filter(entry => entry.trim());
    console.log('Number of font entries found:', fontEntries.length); // Debug log

    return fontEntries.map(entry => {
        console.log('Processing entry:', entry); // Debug log
        const lines = entry.split('\n').map(line => line.trim()).filter(line => line);
        const fontData = {
            font: '',
            location: '',
            characteristics: '',
            confidence: '',
            alternatives: ''
        };

        lines.forEach(line => {
            const lowerLine = line.toLowerCase();
            if (lowerLine.startsWith('font:')) {
                fontData.font = line.replace(/^font:\s*/i, '').trim();
            } else if (lowerLine.startsWith('location:')) {
                fontData.location = line.replace(/^location:\s*/i, '').trim();
            } else if (lowerLine.startsWith('characteristics:')) {
                fontData.characteristics = line.replace(/^characteristics:\s*/i, '').trim();
            } else if (lowerLine.startsWith('confidence:')) {
                fontData.confidence = line.replace(/^confidence:\s*/i, '').trim();
            } else if (lowerLine.startsWith('alternatives:')) {
                fontData.alternatives = line.replace(/^alternatives:\s*/i, '').trim();
            }
        });

        console.log('Parsed font data:', fontData); // Debug log
        return fontData;
    }).filter(data => data.font); // Only keep entries that have a font name
}

// Function to capture the screen and analyze fonts
export async function captureAndAnalyzeFont() {
    const loadingMessage = document.getElementById('loading-message4');
    const outputContainer = document.getElementById('analysisOutput1');

    try {
        // Step 1: Show the loading message
        loadingMessage.style.display = 'block';
        outputContainer.style.display = 'none';

        // Step 2: Capture the visible tab
        const screenshotDataUrl = await chrome.tabs.captureVisibleTab(null, { format: 'png' });

        if (!screenshotDataUrl) {
            console.error('Failed to capture tab image.');
            loadingMessage.style.display = 'none';
            return;
        }

        // Step 3: Call the Gemini API to analyze the font
        const promptText = `You are a font identification expert. Analyze this image and identify all the fonts used in it. For each font you identify:

1. Provide the exact font name (be as specific as possible)
2. Describe where it appears in the image (e.g., "main heading", "navigation menu", "body text")
3. Note any specific characteristics (e.g., "bold", "italic", "light weight", "sans-serif")
4. Rate your confidence in the identification (High/Medium/Low)
5. If confidence is not High, suggest similar alternatives

Format your response EXACTLY like this example (including the blank lines between entries):

Font: Roboto
Location: Main navigation menu
Characteristics: Bold, sans-serif, uppercase
Confidence: High
Alternatives: 

Font: Georgia
Location: Body text paragraphs
Characteristics: Regular weight, serif, 16px
Confidence: Medium
Alternatives: Merriweather, Source Serif Pro

Important:
- Be extremely specific with font names
- Include all visible fonts, even if you're not 100% sure
- Provide Google Fonts alternatives when possible
- Use the exact format shown above
- Include blank lines between each font entry`;

        const analysisResult = await analyzeImageWithAgno(screenshotDataUrl, promptText);
        console.log('Analysis result received:', analysisResult); // Debug log

        // Step 4: Hide loading message and show result
        loadingMessage.style.display = 'none';
        outputContainer.style.display = 'block';

        // Step 5: Parse and display results in cards
        if (analysisResult) {
            // Clear previous content
            outputContainer.innerHTML = '';

            // Create container for cards
            const cardsContainer = document.createElement('div');
            cardsContainer.style.cssText = `
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
                padding: 20px;
            `;

            // Parse and create cards
            const fontDataArray = parseAnalysisResult(analysisResult);
            console.log('Parsed font data array:', fontDataArray); // Debug log

            if (fontDataArray.length === 0) {
                outputContainer.innerHTML = '<p style="text-align: center; color: #666;">No fonts detected. Please try again with a different image or area.</p>';
            } else {
                fontDataArray.forEach(fontData => {
                    const card = createFontCard(fontData);
                    cardsContainer.appendChild(card);
                });
                outputContainer.appendChild(cardsContainer);
            }
        } else {
            outputContainer.innerHTML = '<p style="text-align: center; color: #666;">No font information found. Please try again.</p>';
        }
    } catch (error) {
        console.error('Error analyzing font:', error);
        loadingMessage.style.display = 'none';
        outputContainer.style.display = 'block';
        outputContainer.innerHTML = '<p style="text-align: center; color: #dc3545;">An error occurred during font analysis. Please try again.</p>';
    }
}
