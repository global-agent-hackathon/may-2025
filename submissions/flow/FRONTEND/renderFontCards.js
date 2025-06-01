// Function to load Google Font
async function loadGoogleFont(fontUrl) {
    return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.href = fontUrl;
        link.rel = 'stylesheet';
        link.onload = () => resolve();
        link.onerror = () => reject();
        document.head.appendChild(link);
    });
}

// Function to render font cards
export async function renderFontCards(fontLinks, container) {
    container.innerHTML = ''; // Clear existing cards

    // Load all fonts first
    try {
        await Promise.all(fontLinks.map(link => loadGoogleFont(link)));
    } catch (error) {
        console.error('Error loading fonts:', error);
    }

    fontLinks.forEach(link => {
        // Extract font name from the URL
        const match = link.match(/family=([^:&]+)/);
        let fontName = '';

        if (match) {
            fontName = decodeURIComponent(match[1].replace(/\+/g, ' '));
            fontName = fontName.replace(/:[^,]+/g, '').trim();
        }

        if (fontName) {
            const fontCard = document.createElement('div');
            fontCard.className = 'font-card';
            fontCard.style.cssText = `
                padding: 15px;
                border: 1.5px solid #ccc;
                border-radius: 1rem;
                width: 200px;
                text-align: center;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                background-color: #f5f5f5;
                margin: 10px;
                transition: all 0.3s ease;
            `;

            fontCard.addEventListener('mouseover', () => {
                fontCard.style.boxShadow = '0 0 1px 1px rgba(138, 43, 226, 0.8)';
                fontCard.style.border = '1.5px solid rgba(138, 43, 226, 0.8)';
            });

            fontCard.addEventListener('mouseout', () => {
                fontCard.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
                fontCard.style.border = '1.5px solid #ccc';
            });

            // Create a preview text element
            const previewText = document.createElement('div');
            previewText.textContent = 'The quick brown fox jumps over the lazy dog';
            previewText.style.cssText = `
                font-family: '${fontName}', sans-serif;
                font-size: 16px;
                margin: 10px 0;
                line-height: 1.4;
                min-height: 44px;
            `;

            const fontNameElement = document.createElement('h3');
            fontNameElement.textContent = fontName;
            fontNameElement.style.cssText = `
                font-size: 18px;
                font-weight: normal;
                font-family: '${fontName}', sans-serif;
                margin: 0;
                padding: 5px 0;
            `;

            // Create Apply Font button
            const applyFontBtn = document.createElement('button');
            applyFontBtn.textContent = 'Apply Font';
            applyFontBtn.style.cssText = `
                color: #0a5ecb;
                text-decoration: none;
                display: block;
                margin-top: 10px;
                font-family: Arial, sans-serif;
                font-size: 14px;
                padding: 8px 16px;
                border: 1px solid #0a5ecb;
                border-radius: 15px;
                background: transparent;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
            `;

            applyFontBtn.addEventListener('mouseover', () => {
                applyFontBtn.style.backgroundColor = 'rgba(10, 94, 203, 0.1)';
            });

            applyFontBtn.addEventListener('mouseout', () => {
                applyFontBtn.style.backgroundColor = 'transparent';
            });

            applyFontBtn.onclick = async () => {
                applyFontBtn.disabled = true;
                applyFontBtn.textContent = 'Applying...';

                try {
                    // First inject the font
                    const fontUrl = link;
                    const fontName = fontNameElement.textContent;

                    // Create the CSS to apply the font
                    const css = `
                        * {
                            font-family: '${fontName}', sans-serif !important;
                        }
                    `;

                    // Get the active tab
                    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                    
                    // Inject the font using the scripting API
                    await chrome.scripting.executeScript({
                        target: { tabId: tab.id },
                        func: (fontUrl, fontName, css) => {
                            // First inject the font
                            const link = document.createElement('link');
                            link.href = fontUrl;
                            link.rel = 'stylesheet';
                            document.head.appendChild(link);

                            // Then apply the font
                            const style = document.createElement('style');
                            style.textContent = css;
                            document.head.appendChild(style);
                        },
                        args: [fontUrl, fontName, css]
                    });

                    applyFontBtn.textContent = 'Font Applied!';
                } catch (error) {
                    console.error('Error applying font:', error);
                    applyFontBtn.textContent = 'Failed to Apply';
                }

                setTimeout(() => {
                    applyFontBtn.textContent = 'Apply Font';
                    applyFontBtn.disabled = false;
                }, 2000);
            };

            fontCard.appendChild(fontNameElement);
            fontCard.appendChild(previewText);
            fontCard.appendChild(applyFontBtn);

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
                const urlFontName = fontName.replace(/\s+/g, '+');
                const payload = {
                    prompt: `Go to \"https://fonts.google.com/specimen/${urlFontName}\" and scroll down and click on 'Get Font' Button and then click on 'Download all' Button.`
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
            fontCard.appendChild(downloadBtn);

            container.appendChild(fontCard);
        }
    });

    container.style.display = 'flex';
    container.style.flexWrap = 'wrap';
    container.style.justifyContent = 'center';
    container.style.gap = '20px';
}
