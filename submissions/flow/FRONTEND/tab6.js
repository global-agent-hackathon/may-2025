import { fetchAiResponse } from './fetchAiResponse.js';

// Simple markdown parser function
function parseMarkdown(text) {
    // Convert headers
    text = text.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gm, '<h1>$1</h1>');

    // Convert bold and italic
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Convert lists
    text = text.replace(/^\s*[-*+]\s+(.*$)/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

    // Convert numbered lists
    text = text.replace(/^\s*\d+\.\s+(.*$)/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>)/gs, '<ol>$1</ol>');

    // Convert links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

    // Convert paragraphs
    text = text.replace(/^(?!<[a-z])(.*$)/gm, '<p>$1</p>');

    // Clean up empty paragraphs
    text = text.replace(/<p><\/p>/g, '');

    return text;
}

export function initializeTab6() {
    console.log('Initializing Tab6...');

    // Get DOM elements
    const contentBtn = document.getElementById('contentBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const generateContentForm = document.getElementById('generate-content-form');
    const analyzeContentForm = document.getElementById('analyze-content-form');
    const submitContent = document.getElementById('submitContent');
    const submitAnalysis = document.getElementById('submitAnalysis');
    const loadingMessage = document.getElementById('loading-message6');
    const contentOutput = document.getElementById('contentOutput');
    const contentOutputText = document.getElementById('contentOutputText');
    const copyContentBtn = document.getElementById('copyContentBtn');

    // Function to switch between content generation and analysis modes
    function switchMode(mode) {
        // Hide all forms first
        generateContentForm.style.display = 'none';
        analyzeContentForm.style.display = 'none';
        contentOutput.style.display = 'none';
        loadingMessage.style.display = 'none';

        // Show selected form
        if (mode === 'content') {
            generateContentForm.style.display = 'block';
        } else if (mode === 'analyze') {
            analyzeContentForm.style.display = 'block';
        }
    }

    // Event listeners for mode switching
    contentBtn.addEventListener('click', () => {
        document.querySelectorAll('#capture-container button').forEach(btn => {
            btn.classList.remove('active');
            btn.style.backgroundColor = 'white';
            btn.style.color = 'black';
        });
        contentBtn.classList.add('active');
        contentBtn.style.backgroundColor = '#0a5ecb';
        contentBtn.style.color = 'white';
        switchMode('content');
    });

    analyzeBtn.addEventListener('click', () => {
        document.querySelectorAll('#capture-container button').forEach(btn => {
            btn.classList.remove('active');
            btn.style.backgroundColor = 'white';
            btn.style.color = 'black';
        });
        analyzeBtn.classList.add('active');
        analyzeBtn.style.backgroundColor = '#0a5ecb';
        analyzeBtn.style.color = 'white';
        switchMode('analyze');
    });

    // Handle content generation
    submitContent.addEventListener('click', async () => {
        const contentType = document.getElementById('contentType').value;
        const contentInput = document.getElementById('contentInput').value;

        if (!contentInput) {
            alert('Please enter a topic or description.');
            return;
        }

        loadingMessage.style.display = 'block';
        contentOutput.style.display = 'none';

        try {
            let promptText = '';
            switch (contentType) {
            // Content Writing
            case 'blog':
                promptText = `Write a professional blog post about "${contentInput}". Include an engaging introduction, main points with examples, and a conclusion. Format with markdown.`;
                break;
            case 'article':
                promptText = `Write a well-researched article about "${contentInput}". Include relevant statistics, expert opinions, and practical insights. Format with markdown.`;
                break;
            case 'newsletter':
                promptText = `Create an engaging newsletter about "${contentInput}". Include a compelling subject line, main content, and call-to-action. Format with markdown.`;
                break;
            case 'social':
                promptText = `Create an engaging social media post about "${contentInput}". Include relevant hashtags and emojis. Make it attention-grabbing and shareable.`;
                break;

                // Business Writing
            case 'email':
                promptText = `Write a professional email about "${contentInput}". Include a clear subject line, greeting, body, and closing. Make it concise and actionable.`;
                break;
            case 'proposal':
                promptText = `Write a business proposal about "${contentInput}". Include executive summary, objectives, methodology, timeline, and budget. Format with markdown.`;
                break;
            case 'product':
                promptText = `Write a compelling product description for "${contentInput}". Highlight key features, benefits, and use cases. Make it persuasive and SEO-friendly.`;
                break;
            case 'case-study':
                promptText = `Write a case study about "${contentInput}". Include background, challenge, solution, and results. Format with markdown.`;
                break;

                // Creative Writing
            case 'story':
                promptText = `Write a short story about "${contentInput}". Include character development, plot, and a satisfying conclusion. Format with markdown.`;
                break;
            case 'script':
                promptText = `Write a video script about "${contentInput}". Include scene descriptions, dialogue, and camera directions. Format with markdown.`;
                break;
            case 'poem':
                promptText = `Write a poem about "${contentInput}". Use creative language and emotional depth. Format with markdown.`;
                break;
            case 'dialogue':
                promptText = `Write a dialogue about "${contentInput}". Include natural conversation flow and character voice. Format with markdown.`;
                break;

                // Professional
            case 'resume':
                promptText = `Write a professional resume summary for "${contentInput}". Highlight key achievements and skills. Format with markdown.`;
                break;
            case 'cover-letter':
                promptText = `Write a compelling cover letter for "${contentInput}". Include relevant experience and enthusiasm. Format with markdown.`;
                break;
            case 'bio':
                promptText = `Write a professional bio for "${contentInput}". Include background, expertise, and personality. Format with markdown.`;
                break;
            case 'portfolio':
                promptText = `Write a portfolio description for "${contentInput}". Highlight key projects and achievements. Format with markdown.`;
                break;
            }

            const result = await fetchAiResponse(promptText);
            contentOutputText.innerHTML = parseMarkdown(result);
            contentOutput.style.display = 'block';
        } catch (error) {
            console.error('Error generating content:', error);
            contentOutputText.innerHTML = 'An error occurred. Please try again.';
            contentOutput.style.display = 'block';
        } finally {
            loadingMessage.style.display = 'none';
        }
    });

    // Handle content analysis
    submitAnalysis.addEventListener('click', async () => {
        const analysisType = document.getElementById('analysisType').value;
        const analyzeInput = document.getElementById('analyzeInput').value;

        if (!analyzeInput) {
            alert('Please enter content to analyze.');
            return;
        }

        loadingMessage.style.display = 'block';
        contentOutput.style.display = 'none';

        try {
            let promptText = '';
            switch (analysisType) {
            // Content Analysis
            case 'sentiment':
                promptText = `Analyze the sentiment of this text and provide a detailed breakdown of the emotional tone, key phrases that contribute to the sentiment, and suggestions for improvement if needed: "${analyzeInput}"`;
                break;
            case 'keywords':
                promptText = `Extract the main keywords and key phrases from this text, categorize them by importance, and explain their relevance: "${analyzeInput}"`;
                break;
            case 'summary':
                promptText = `Provide a concise summary of this text, highlighting the main points and key takeaways: "${analyzeInput}"`;
                break;
            case 'grammar':
                promptText = `Check this text for grammar, spelling, and punctuation errors. Provide corrections and suggestions for improvement: "${analyzeInput}"`;
                break;

                // SEO & Marketing
            case 'seo':
                promptText = `Analyze this content for SEO optimization. Provide keyword density, meta description suggestions, and recommendations for improvement: "${analyzeInput}"`;
                break;
            case 'readability':
                promptText = `Calculate the readability score of this text and provide suggestions to improve clarity and accessibility: "${analyzeInput}"`;
                break;
            case 'engagement':
                promptText = `Predict the potential engagement of this content and suggest ways to increase reader interaction: "${analyzeInput}"`;
                break;
            case 'competitor':
                promptText = `Analyze this content in comparison to industry standards and provide competitive insights: "${analyzeInput}"`;
                break;

                // Writing Enhancement
            case 'tone':
                promptText = `Analyze the tone of this text and suggest adjustments to better match the intended audience and purpose: "${analyzeInput}"`;
                break;
            case 'style':
                promptText = `Review the writing style of this text and provide suggestions for improvement in clarity, consistency, and impact: "${analyzeInput}"`;
                break;
            case 'plagiarism':
                promptText = `Check this text for potential plagiarism issues and suggest ways to make it more original: "${analyzeInput}"`;
                break;
            case 'improve':
                promptText = `Provide specific suggestions to improve this content's quality, engagement, and effectiveness: "${analyzeInput}"`;
                break;

                // Business Metrics
            case 'conversion':
                promptText = `Analyze this content's potential for conversion and suggest optimization strategies: "${analyzeInput}"`;
                break;
            case 'audience':
                promptText = `Analyze the target audience of this content and suggest ways to better engage them: "${analyzeInput}"`;
                break;
            case 'trend':
                promptText = `Analyze this content's alignment with current trends and suggest relevant updates: "${analyzeInput}"`;
                break;
            case 'roi':
                promptText = `Evaluate the potential ROI of this content and suggest ways to maximize its impact: "${analyzeInput}"`;
                break;
            }

            const result = await fetchAiResponse(promptText);
            contentOutputText.innerHTML = parseMarkdown(result);
            contentOutput.style.display = 'block';
        } catch (error) {
            console.error('Error analyzing content:', error);
            contentOutputText.innerHTML = 'An error occurred. Please try again.';
            contentOutput.style.display = 'block';
        } finally {
            loadingMessage.style.display = 'none';
        }
    });

    // Handle copy button click
    copyContentBtn.addEventListener('click', async () => {
        try {
            // Get the text content without HTML tags
            const textToCopy = contentOutputText.innerText;
            await navigator.clipboard.writeText(textToCopy);

            // Show feedback
            const originalText = copyContentBtn.innerHTML;
            copyContentBtn.innerHTML = `
                <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 24 24">
                    <path fill-rule="evenodd" d="M2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10S2 17.523 2 12Zm13.707-1.293a1 1 0 0 0-1.414-1.414L11 12.586l-1.293-1.293a1 1 0 0 0-1.414 1.414l2 2a1 1 0 0 0 1.414 0l4-4Z" clip-rule="evenodd"/>
                </svg>
                Copied!
            `;

            // Reset button after 2 seconds
            setTimeout(() => {
                copyContentBtn.innerHTML = originalText;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy text to clipboard');
        }
    });

    // Initialize with no mode selected
    document.querySelectorAll('#capture-container button').forEach(btn => {
        btn.classList.remove('active');
        btn.style.backgroundColor = 'white';
        btn.style.color = 'black';
    });

    // Hide all content initially
    generateContentForm.style.display = 'none';
    analyzeContentForm.style.display = 'none';
    contentOutput.style.display = 'none';
    loadingMessage.style.display = 'none';
}
