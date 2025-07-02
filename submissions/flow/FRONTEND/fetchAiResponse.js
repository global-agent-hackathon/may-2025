// frontend/utils/fetchAiResponse.js
export async function fetchAiResponse(prompt) {
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
