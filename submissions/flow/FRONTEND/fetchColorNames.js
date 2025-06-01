export async function fetchColorNames(hexCodes) {
    const url = `https://api.color.pizza/v1/?values=${hexCodes.join(',')}`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log('API response:', data);

        const colorNames = data.colors.map(color => color.name);
        if (colorNames.length === 0) {
            throw new Error('No colors returned from the API.');
        }

        console.log('Colors for analysis:', colorNames.join(', '));
        return colorNames;
    } catch (error) {
        console.error('Error fetching color names:', error);
        throw new Error('Failed to retrieve color names.');
    }
}
