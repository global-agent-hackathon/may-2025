document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const prototypeForm = document.getElementById('prototype-form');
    const loadingSection = document.getElementById('loading');
    const resultSection = document.getElementById('result-section');
    const codeDisplay = document.getElementById('code-display');
    const codeTitle = document.getElementById('code-title');
    const fileInfo = document.getElementById('file-info');
    const analysisContent = document.getElementById('analysis-content');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            
            // Update active tab button
            tabBtns.forEach(btn => btn.classList.remove('active'));
            btn.classList.add('active');
            
            // Show corresponding tab content
            tabContents.forEach(tab => {
                if (tab.id === `${tabName}-tab`) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });
        });
    });

    // Copy code to clipboard
    copyBtn.addEventListener('click', () => {
        const code = codeDisplay.textContent;
        navigator.clipboard.writeText(code)
            .then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Could not copy text: ', err);
                alert('Failed to copy code to clipboard');
            });
    });

    // Download code as file
    downloadBtn.addEventListener('click', () => {
        const code = codeDisplay.textContent;
        const prototypeType = prototypeForm.type.value;
        let filename = '';
        let mimeType = '';
        
        // Determine filename and mime type based on prototype type
        if (prototypeType === 'webapp') {
            filename = 'prototype.html';
            mimeType = 'text/html';
        } else {
            filename = 'prototype.py';
            mimeType = 'text/plain';
        }
        
        // Create a blob from the code
        const blob = new Blob([code], { type: mimeType });
        
        // Create a URL for the blob
        const url = URL.createObjectURL(blob);
        
        // Create a download link and trigger it
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    });

    // Form submission
    prototypeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(prototypeForm);
        const prompt = formData.get('prompt');
        const type = formData.get('type');
        
        // Show loading, hide results
        loadingSection.classList.remove('hidden');
        resultSection.classList.add('hidden');
        
        try {
            // Send request to the API
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt, type })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Hide loading, show results
            loadingSection.classList.add('hidden');
            resultSection.classList.remove('hidden');
            
            // Update code display
            codeDisplay.textContent = data.code;
            
            // Set code language class based on prototype type
            if (data.prototype_type === 'webapp') {
                codeDisplay.className = 'language-html';
                codeTitle.textContent = 'Web Application';
            } else if (data.prototype_type === 'script') {
                codeDisplay.className = 'language-python';
                codeTitle.textContent = 'Python Script';
            } else {
                codeDisplay.className = 'language-python';
                codeTitle.textContent = 'Command-line Utility';
            }
            
            // Apply syntax highlighting
            hljs.highlightElement(codeDisplay);
            
            // Show file info
            fileInfo.textContent = `Saved to: ${data.file_path}`;
            
            // Show analysis
            analysisContent.innerHTML = data.analysis.replace(/\n/g, '<br>');
            
        } catch (error) {
            console.error('Error generating prototype:', error);
            loadingSection.classList.add('hidden');
            alert(`Error generating prototype: ${error.message}`);
        }
    });
}); 