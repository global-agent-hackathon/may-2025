export async function analyzeImageWithAgno(imageDataUrl, prompt) {
    const serverApiUrl = 'http://127.0.0.1:5000/api/ai-response'; // Update if deployed elsewhere

    try {
        const response = await fetch(serverApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                image_url: imageDataUrl // direct URL or data URL
            })
        });

        if (!response.ok) {
            console.error('Server request failed:', response.statusText);
            throw new Error('Server request failed');
        }

        const result = await response.json();
        console.log('Server Image Analysis Result:', result.response);
        return result.response;

    } catch (error) {
        console.error('Error analyzing image via server:', error);
        throw new Error('Error analyzing image via server');
    }
}
