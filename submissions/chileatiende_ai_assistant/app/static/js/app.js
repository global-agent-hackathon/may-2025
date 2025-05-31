document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM completamente cargado y analizado. Inicializando app de chat.");
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const loadingIndicator = document.getElementById('loading-indicator');

    // Variable para controlar si la síntesis de voz está activa
    let speechSynthesis = window.speechSynthesis;
    let currentUtterance = null;

    // Ajustar altura del textarea dinámicamente
    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    function appendMessage(sender, text, isHtml = false) {
        const msgArticle = document.createElement('article');
        msgArticle.classList.add('chat-message', sender);
        console.log(`Añadiendo mensaje de ${sender}:`, isHtml ? "(HTML)" : text);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message');

        if (sender === 'bot' && isHtml) {
            contentDiv.innerHTML = text; // HTML sanitizado para mitigar XSS
        } else {
            contentDiv.textContent = text;
        }
        
        msgArticle.appendChild(contentDiv);

        // Añadir botón de audio solo para mensajes del bot
        if (sender === 'bot') {
            const audioButton = document.createElement('button');
            audioButton.classList.add('audio-button');
            audioButton.setAttribute('aria-label', 'Reproducir mensaje en voz alta');
            audioButton.innerHTML = `
                <svg class="speaker-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <path class="sound-waves" d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                </svg>
            `;
            
            // Obtener el texto plano del mensaje para la síntesis de voz
            const plainText = contentDiv.textContent || contentDiv.innerText;
            
            audioButton.addEventListener('click', function() {
                toggleSpeech(plainText, audioButton);
            });
            
            msgArticle.appendChild(audioButton);
        }

        chatWindow.appendChild(msgArticle);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Mantener el scroll abajo
    }

    function toggleSpeech(text, button) {
        // Si hay una síntesis en curso, detenerla
        if (speechSynthesis.speaking) {
            speechSynthesis.cancel();
            console.log("Síntesis de voz detenida.");
            // Si el botón actual es el mismo que inició la síntesis, solo detener
            if (button.classList.contains('speaking')) {
                button.classList.remove('speaking');
                return;
            }
            // Si es un botón diferente, quitar la clase del anterior
            document.querySelectorAll('.audio-button.speaking').forEach(btn => {
                btn.classList.remove('speaking');
            });
        }

        // Crear nueva síntesis de voz
        console.log("Iniciando síntesis de voz para el texto:", text.substring(0, 50) + "...");
        currentUtterance = new SpeechSynthesisUtterance(text);
        currentUtterance.lang = 'es-ES'; // Español
        currentUtterance.rate = 1.0; // Velocidad normal
        currentUtterance.pitch = 1.2; // Tono ligeramente más alto

        // Marcar el botón como activo
        button.classList.add('speaking');

        // Eventos de la síntesis
        currentUtterance.onend = function() {
            button.classList.remove('speaking');
            console.log("Síntesis de voz finalizada.");
        };

        currentUtterance.onerror = function(event) {
            button.classList.remove('speaking');
            console.error('Error en la síntesis de voz:', event.error);
        };

        // Iniciar la síntesis
        speechSynthesis.speak(currentUtterance);
    }

    function showLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.style.display = 'block';
            sendBtn.disabled = true;
            userInput.disabled = true;
            console.log("Mostrando indicador de carga.");
        } else {
            loadingIndicator.style.display = 'none';
            sendBtn.disabled = false;
            userInput.disabled = false;
            userInput.focus();
            console.log("Ocultando indicador de carga.");
        }
    }

    async function handleSendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        console.log("Enviando mensaje del usuario:", text);
        appendMessage('user', text);
        userInput.value = '';
        userInput.style.height = 'auto'; // Resetear altura del textarea

        showLoading(true);

        try {
            const res = await fetch('/api/chat', { // Endpoint de la API
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            
            if (!res.ok) {
                let errorMsg = `Error del servidor: ${res.status}`;
                try {
                    const errorData = await res.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (e) { /* No hacer nada si el cuerpo del error no es JSON */ }
                throw new Error(errorMsg);
            }

            const data = await res.json();
            if (data.error) {
                appendMessage('bot', `Error: ${data.error}`);
                console.error("Error recibido del backend:", data.error);
            } else {
                // Convertir Markdown a HTML y sanitizarlo para mitigar XSS antes de insertarlo
                const htmlResponse = marked.parse(data.response);
                const safeHtml = DOMPurify.sanitize(htmlResponse);
                appendMessage('bot', safeHtml, true);
                console.log("Respuesta del bot (HTML) recibida y añadida al chat.");
            }
        } catch (e) {
            appendMessage('bot', `Error de comunicación: ${e.message}`);
            console.error("Error de comunicación en handleSendMessage:", e);
        } finally {
            showLoading(false);
        }
    }

    sendBtn.addEventListener('click', handleSendMessage);

    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    userInput.focus(); // Enfocar el input al cargar la página

    // Añadir funcionalidad al botón de audio del mensaje inicial
    const initialAudioButton = document.querySelector('.chat-message.bot .audio-button');
    if (initialAudioButton) {
        const initialMessageElement = document.querySelector('.chat-message.bot .message');
        if (initialMessageElement) {
            const initialMessage = initialMessageElement.textContent || initialMessageElement.innerText;
            initialAudioButton.addEventListener('click', function() {
                toggleSpeech(initialMessage, initialAudioButton);
                console.log("Reproduciendo mensaje inicial del bot.");
            });
        }
    }
}); 