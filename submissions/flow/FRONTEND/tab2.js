import { analyzeColors } from './analyzeColors.js';
import { captureTabColors } from './captureTabColors.js';
import { renderColorPalette } from './renderColorPalette.js';
import { updatePalette } from './updateColorPalette.js';
import { fetchAiResponse } from './fetchAiResponse.js';

export function initializeTab2() {
    const captureBtn = document.getElementById('captureBtn');
    const aiBtn = document.getElementById('aiBtn');
    const paletteContainer = document.getElementById('palette-container');
    const paletteCard = document.getElementById('palette-card');
    const screenInfoCard = document.getElementById('screen-info-card');
    const submitPalette = document.getElementById('submitPalette');
    const loadingMessage = document.getElementById('loading-message');
    const generatePaletteForm = document.getElementById('generate-palette-form');
    const savedPalettesContainer = document.getElementById('saved-palettes-container');
    const editPaletteBtn = document.getElementById('editPaletteBtn');
    const morePaletteBtn = document.getElementById('morePaletteBtn');
    const streamedTextContainer = document.getElementById('streamed-text');

    let isEditMode = false;

    // Event listener for the capture button
    captureBtn.addEventListener('click', () => {
        // Remove active class from all buttons in capture-container
        document.querySelectorAll('#capture-container button').forEach(btn => btn.classList.remove('active'));
        // Add active class to clicked button
        captureBtn.classList.add('active');
        captureTabColors();
    });

    // Event listener for the AI button
    aiBtn.addEventListener('click', () => {
        // Remove active class from all buttons in capture-container
        document.querySelectorAll('#capture-container button').forEach(btn => btn.classList.remove('active'));
        // Add active class to clicked button
        aiBtn.classList.add('active');

        // Hide other containers
        paletteCard.style.display = 'none';
        savedPalettesContainer.style.display = 'none';
        screenInfoCard.style.display = 'none';

        // Show the generate palette form
        generatePaletteForm.style.display = 'block';
    });

    // Event listener for the saved palette button
    document.getElementById('savedPaletteBtn').addEventListener('click', () => {
        // Remove active class from all buttons in capture-container
        document.querySelectorAll('#capture-container button').forEach(btn => btn.classList.remove('active'));
        // Add active class to clicked button
        document.getElementById('savedPaletteBtn').classList.add('active');

        // Show saved palettes container
        savedPalettesContainer.style.display = 'block';
        // Hide other containers
        paletteCard.style.display = 'none';
        screenInfoCard.style.display = 'none';
        generatePaletteForm.style.display = 'none';
    });

    submitPalette.addEventListener('click', async () => {
        const paletteInput = document.getElementById('paletteInput').value;

        // Display loading message and clear previous text
        loadingMessage.style.display = 'block';
        streamedTextContainer.innerText = ''; // Clear text container
        paletteContainer.innerHTML = ''; // Clear previous color palette
        document.getElementById('palette-container').style.display = 'none'; // Hide the palette initially

        try {
            const promptText = `Generate a color palette with hexcode based on the phrase, not more than 100 words: "${paletteInput}".`;

            // Fetch the AI response
            const result = await fetchAiResponse(promptText);

            // Hide the loading message and show the palette container
            loadingMessage.style.display = 'none';
            document.getElementById('palette-container').style.display = 'block';

            console.log('AI Response:', result);

            // Extract hex color codes from the result
            const hexColorRegex = /#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b/g;
            const hexCodes = result.match(hexColorRegex) || [];
            console.log('Extracted hex codes:', hexCodes);

            // Render the color palette
            renderColorPalette(hexCodes);
        } catch (error) {
            console.error('Error generating color palette:', error);
            loadingMessage.style.display = 'none';
            streamedTextContainer.textContent = 'An error occurred. Please try again.';
        }
    });

    morePaletteBtn.addEventListener('click', () => {
        const screenInfoCard = document.getElementById('screen-info-card');
        const nestedTabContent = document.getElementById('nested-tab-content');
        const resultCard = document.getElementById('resultCard');
        const aiResponseText = document.getElementById('aiResponseText');
        const loadingMessage = document.getElementById('loading-message2');

        // Reset all nested tab buttons without selecting any
        document.querySelectorAll('#screen-info-card .tab-button').forEach(btn => btn.classList.remove('active'));

        // Reset all sub-buttons
        document.querySelectorAll('.sub-button').forEach(btn => btn.classList.remove('selected'));

        // Hide nested tab content initially
        nestedTabContent.style.display = 'none';
        document.getElementById('nestedTab1').style.display = 'none';
        document.getElementById('nestedTab2').style.display = 'none';
        document.getElementById('nestedTab3').style.display = 'none';

        // Clear previous results
        resultCard.style.display = 'none';
        aiResponseText.textContent = '';
        loadingMessage.style.display = 'none';

        // Show the screen info card
        screenInfoCard.style.display = 'block';
    });

    function toggleEditMode() {
        isEditMode = !isEditMode;
        editPaletteBtn.textContent = isEditMode ? 'Exit Edit Mode' : 'Edit Palette';
        updatePalette(isEditMode);
    }

    editPaletteBtn.addEventListener('click', toggleEditMode);
    paletteCard.appendChild(editPaletteBtn);

    // Event listeners for nested tabs
    document.getElementById('nestedTab1Btn').addEventListener('click', () => {
        document.getElementById('nestedTab1Btn').classList.add('active');
        document.getElementById('nestedTab2Btn').classList.remove('active');
        document.getElementById('nestedTab3Btn').classList.remove('active');
        document.getElementById('nested-tab-content').style.display = 'block';
        document.getElementById('nestedTab1').style.display = 'block';
        document.getElementById('nestedTab2').style.display = 'none';
        document.getElementById('nestedTab3').style.display = 'none';
        // Hide loading message and result card when switching tabs
        document.getElementById('loading-message2').style.display = 'none';
        document.getElementById('resultCard').style.display = 'none';
    });

    document.getElementById('nestedTab2Btn').addEventListener('click', () => {
        document.getElementById('nestedTab1Btn').classList.remove('active');
        document.getElementById('nestedTab2Btn').classList.add('active');
        document.getElementById('nestedTab3Btn').classList.remove('active');
        document.getElementById('nested-tab-content').style.display = 'block';
        document.getElementById('nestedTab1').style.display = 'none';
        document.getElementById('nestedTab2').style.display = 'block';
        document.getElementById('nestedTab3').style.display = 'none';
        // Hide loading message and result card when switching tabs
        document.getElementById('loading-message2').style.display = 'none';
        document.getElementById('resultCard').style.display = 'none';
    });

    document.getElementById('nestedTab3Btn').addEventListener('click', () => {
        document.getElementById('nestedTab1Btn').classList.remove('active');
        document.getElementById('nestedTab2Btn').classList.remove('active');
        document.getElementById('nestedTab3Btn').classList.add('active');
        document.getElementById('nested-tab-content').style.display = 'block';
        document.getElementById('nestedTab1').style.display = 'none';
        document.getElementById('nestedTab2').style.display = 'none';
        document.getElementById('nestedTab3').style.display = 'block';
        // Hide loading message and result card when switching tabs
        document.getElementById('loading-message2').style.display = 'none';
        document.getElementById('resultCard').style.display = 'none';
    });

    // Event listeners for each button
    document.getElementById('runAiBtn1').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab1 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn1').classList.add('selected');
        analyzeColors('runAiBtn1', 'Mood of the Color Palette');
    });

    document.getElementById('runAiBtn2').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab1 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn2').classList.add('selected');
        analyzeColors('runAiBtn2', 'Palette Insight based on Industry, be specific');
    });

    document.getElementById('runAiBtn4').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab1 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn4').classList.add('selected');
        analyzeColors('runAiBtn4', 'Provide Cultural significance of the color palette');
    });

    document.getElementById('runAiBtn5').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab2 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn5').classList.add('selected');
        analyzeColors('runAiBtn5', 'Suggest how the colors can be integrated into a logo, emphasizing the emotions or messages that the colors convey. For example, if one of the hex codes is a vibrant blue, recommend using it for trustworthiness, while a warmer hue could highlight creativity or energy.');
    });

    document.getElementById('runAiBtn6').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab2 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn6').classList.add('selected');
        analyzeColors('runAiBtn6', 'Provide options for adapting color use in responsive web designs.');
    });

    document.getElementById('runAiBtn7').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab2 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn7').classList.add('selected');
        analyzeColors('runAiBtn7', ' Suggest how to effectively apply the color scheme in printed materials.');
    });

    document.getElementById('runAiBtn8').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab2 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn8').classList.add('selected');
        analyzeColors('runAiBtn8', 'Provide feedback on color uses in interior design.');
    });

    document.getElementById('runAiBtn9').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab3 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn9').classList.add('selected');
        analyzeColors('runAiBtn9', 'Analyze and verify the contrast ratios of color combinations to ensure text and background colors meet accessibility standards (e.g., WCAG compliance).');
    });

    document.getElementById('runAiBtn10').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab3 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn10').classList.add('selected');
        analyzeColors('runAiBtn10', 'Simulate how the color palette appears to users with different types of color blindness (e.g., deuteranopia, protanopia, tritanopia) and suggest accessible color adjustments.');
    });

    document.getElementById('runAiBtn11').addEventListener('click', () => {
        document.querySelectorAll('#nestedTab3 .sub-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('runAiBtn11').classList.add('selected');
        analyzeColors('runAiBtn11', 'Offer alternative colors that retain the design aesthetic while improving accessibility for visually impaired users.');
    });
}
