// Element Picker Content Script
let pickerActive = false;
let lastElement = null;
let popupDiv = null;
let isTranslationMode = false;
let selectedLanguage = null;

const LANGUAGE_NAMES = {
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'ja': 'Japanese',
    'zh': 'Chinese',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi'
};

function createPopupForElement(el, text = 'Analyze this element?') {
    removePopup();
    const rect = el.getBoundingClientRect();
    popupDiv = document.createElement('div');
    popupDiv.style.position = 'fixed';
    popupDiv.style.left = Math.min(rect.right + 10, window.innerWidth - 220) + 'px';
    popupDiv.style.top = Math.max(rect.top, 10) + 'px';
    popupDiv.style.background = '#fff';
    popupDiv.style.border = '1.5px solid #0a5ecb';
    popupDiv.style.borderRadius = '10px';
    popupDiv.style.padding = '10px 16px';
    popupDiv.style.boxShadow = '0 4px 16px rgba(0,0,0,0.18)';
    popupDiv.style.zIndex = 2147483647;
    popupDiv.style.fontSize = '15px';
    popupDiv.style.color = '#222';
    popupDiv.style.maxWidth = '200px';
    popupDiv.style.pointerEvents = 'none';
    popupDiv.textContent = text;
    document.body.appendChild(popupDiv);
}

function removePopup() {
    if (popupDiv) {
        popupDiv.remove();
        popupDiv = null;
    }
}

function highlightElement(el) {
    if (!el) {
        return;
    }
    el.style.outline = '2.5px solid #0a5ecb';
}

function removeHighlight(el) {
    if (!el) {
        return;
    }
    el.style.outline = '';
}

function onMouseOver(e) {
    if (!pickerActive) {
        return;
    }
    if (lastElement && lastElement !== e.target) {
        removeHighlight(lastElement);
    }
    highlightElement(e.target);
    lastElement = e.target;
    createPopupForElement(e.target, isTranslationMode ? `Translate to ${LANGUAGE_NAMES[selectedLanguage]}?` : 'Analyze this element?');
}

function onMouseOut(e) {
    if (!pickerActive) {
        return;
    }
    removeHighlight(e.target);
}

function onClick(e) {
    if (!pickerActive) {
        return;
    }
    e.preventDefault();
    e.stopPropagation();
    pickerActive = false;
    removeHighlight(e.target);
    document.body.style.cursor = '';
    document.removeEventListener('mouseover', onMouseOver, true);
    document.removeEventListener('mouseout', onMouseOut, true);
    document.removeEventListener('click', onClick, true);

    if (popupDiv) {
        popupDiv.textContent = isTranslationMode ? 'Translating...' : 'Analyzing...';
    }

    const info = {
        tag: e.target.tagName,
        text: e.target.innerText,
        src: e.target.src,
        id: e.target.id,
        class: e.target.className,
        outerHTML: e.target.outerHTML
    };

    const endpoint = isTranslationMode ? '/api/translate' : '/api/ai-response';
    const prompt = isTranslationMode
        ? `Translate this text to ${LANGUAGE_NAMES[selectedLanguage]}. Focus on providing a natural, accurate translation that maintains the original meaning.`
        : 'In one short sentence, what is this image or text about?';

    console.log('Sending translation request:', {
        endpoint,
        prompt,
        language: selectedLanguage,
        languageName: LANGUAGE_NAMES[selectedLanguage]
    });

    fetch(`http://localhost:5000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, element: info })
    })
        .then(res => res.json())
        .then(data => {
            console.log('Translation response:', data);
            if (isTranslationMode && data.translations) {
                // Replace the original text with translation
                const originalText = e.target.innerText;
                const translation = data.translations[0].text;

                // Store original text as a data attribute
                e.target.setAttribute('data-original-text', originalText);

                // Replace the text content
                e.target.innerText = translation;

                // Add a small indicator that this is translated text
                e.target.style.position = 'relative';
                e.target.style.cursor = 'pointer';

                // Add hover effect to show original text
                e.target.onmouseover = () => {
                    e.target.title = `Original: ${originalText}`;
                };

                // Add click handler to toggle between original and translation
                e.target.onclick = (event) => {
                    event.stopPropagation();
                    const currentText = e.target.innerText;
                    const storedOriginal = e.target.getAttribute('data-original-text');

                    if (currentText === storedOriginal) {
                        e.target.innerText = translation;
                    } else {
                        e.target.innerText = storedOriginal;
                    }
                };

                // Remove the popup
                removePopup();
            } else if (popupDiv) {
                popupDiv.textContent = data.response || 'No result available.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (popupDiv) {
                popupDiv.textContent = 'Error processing request';
            }
        });
}

function startElementPicker(mode = 'analyze', language = null) {
    pickerActive = true;
    isTranslationMode = mode === 'translate';
    selectedLanguage = language;
    document.body.style.cursor = 'crosshair';
    document.addEventListener('mouseover', onMouseOver, true);
    document.addEventListener('mouseout', onMouseOut, true);
    document.addEventListener('click', onClick, true);

    // Add click listener to document to close popup when clicking anywhere
    document.addEventListener('click', function closePopup(e) {
        if (popupDiv && !popupDiv.contains(e.target)) {
            removePopup();
            document.removeEventListener('click', closePopup);
        }
    });
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === 'startElementPicker') {
        startElementPicker(msg.mode || 'analyze', msg.language);
        sendResponse({ status: 'started', mode: msg.mode, language: msg.language });
    }
    return true;
});
