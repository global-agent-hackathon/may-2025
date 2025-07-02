// Get references to HTML elements
import { renderColorPalette } from './renderColorPalette.js';

const paletteContainer = document.getElementById('palette-container');
const paletteCard = document.getElementById('palette-card');
const screenInfoCard = document.getElementById('screen-info-card');
const generatePaletteForm = document.getElementById('generate-palette-form');
const savePaletteBtn = document.getElementById('savePaletteBtn');
const savedPaletteBtn = document.getElementById('savedPaletteBtn');
const savedPalettesContainer = document.getElementById('saved-palettes-container');
const savedPalettesDiv = document.getElementById('savedPalettes');

// Display saved palettes when savedPaletteBtn is clicked
savedPaletteBtn.addEventListener('click', toggleSavedPalettes);

function toggleSavedPalettes() {
    // Load and display saved palettes from local storage
    displaySavedPalettes();

    // Toggle the visibility of saved-palettes-container
    savedPalettesContainer.style.display = savedPalettesContainer.style.display === 'none' ? 'block' : 'none';
}

function displaySavedPalettes() {
    if (!savedPalettesDiv || !generatePaletteForm || !paletteCard || !screenInfoCard) {
        console.error('One or more required elements are missing from the DOM.');
        return; // Exit the function early if elements are not available
    }

    // Clear previously displayed palettes
    savedPalettesDiv.innerHTML = '';
    generatePaletteForm.style.display = 'none';
    paletteCard.style.display = 'none';
    screenInfoCard.style.display = 'none';

    // Retrieve saved palettes from local storage
    const savedPalettes = JSON.parse(localStorage.getItem('savedPalettes')) || [];

    if (savedPalettes.length === 0) {
        savedPalettesDiv.innerHTML = '<p>No saved palettes found.</p>';
    } else {
        savedPalettes.forEach((palette, index) => {
            // Create a div for each saved palette
            const paletteDiv = document.createElement('div');
            paletteDiv.className = 'saved-palette';
            paletteDiv.style.display = 'flex';
            paletteDiv.style.alignItems = 'center';
            paletteDiv.style.marginBottom = '10px';

            // Add each color as a swatch in the palette div
            palette.forEach(color => {
                const colorDiv = document.createElement('div');
                colorDiv.style.width = '30px';
                colorDiv.style.height = '30px';
                colorDiv.style.backgroundColor = color;
                colorDiv.style.marginRight = '5px';
                colorDiv.title = color;
                paletteDiv.appendChild(colorDiv);
            });

            // Create a delete button with an SVG icon
            const deleteButton = document.createElement('button');
            deleteButton.style.marginLeft = '10px';
            deleteButton.innerHTML = `
                <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m15 9-6 6m0-6 6 6m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
                </svg>
            `;

            deleteButton.onclick = (function (index) {
                return function (event) {
                    event.stopPropagation(); // Prevent triggering the paletteDiv click event
                    deletePalette(index);
                };
            })(index);

            paletteDiv.appendChild(deleteButton);

            // Add click event to display the palette if not clicking the delete button
            paletteDiv.addEventListener('click', (event) => {
                if (event.target !== deleteButton) { // Ensure click is not on delete button
                    renderColorPalette(palette);
                    savedPalettesContainer.style.display = 'none';
                }
            });

            // Append each palette row to savedPalettesDiv
            savedPalettesDiv.appendChild(paletteDiv);
        });
    }
}

function deletePalette(index) {
    // Retrieve saved palettes from local storage
    const savedPalettes = JSON.parse(localStorage.getItem('savedPalettes')) || [];

    if (index >= 0 && index < savedPalettes.length) {  // Check if index is valid
        // Remove the palette at the specified index
        savedPalettes.splice(index, 1);
        console.log('Updated palettes after deletion:', savedPalettes); // Debugging line

        // Update local storage with the modified palettes
        localStorage.setItem('savedPalettes', JSON.stringify(savedPalettes));

        // Refresh the displayed palettes
        displaySavedPalettes();
    } else {
        console.error('Invalid index for deletion:', index); // Debugging error message
    }
}

// Event listener to save the current palette
savePaletteBtn.addEventListener('click', savePalette);

function savePalette() {
    const colors = Array.from(paletteContainer.children).map(div => div.getAttribute('data-hex'));
    const savedMessage = document.getElementById('saved-message');

    if (colors.length > 0) {
        // Retrieve saved palettes from local storage, or initialize an empty array
        const savedPalettes = JSON.parse(localStorage.getItem('savedPalettes')) || [];

        // Add the new palette
        savedPalettes.push(colors);

        // Update local storage with the new list of palettes
        localStorage.setItem('savedPalettes', JSON.stringify(savedPalettes));

        savedMessage.style.display = 'block';
        setTimeout(() => {
            savedMessage.style.display = 'none';
        }, 2000);
    } else {
        alert('No colors to save.');
    }
}
