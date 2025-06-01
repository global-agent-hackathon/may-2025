export function renderColorPalette(colors) {

    const paletteContainer = document.getElementById('palette-container');
    const copiedMessage = document.getElementById('copied-message');
    const paletteCard = document.getElementById('palette-card');
    const isEditMode = false;

    paletteContainer.innerHTML = ''; // Clear previous palette

    if (colors.length === 0) {
        paletteContainer.innerHTML = '<p>No colors found.</p>';
        return;
    }

    colors.forEach(hexCode => {
        const colorDiv = document.createElement('div');
        colorDiv.style.backgroundColor = hexCode;
        colorDiv.className = 'color-box';
        colorDiv.style.position = 'relative';
        colorDiv.setAttribute('data-hex', hexCode);

        const hexCodeDisplay = document.createElement('div');
        hexCodeDisplay.textContent = hexCode;
        hexCodeDisplay.style.position = 'absolute';
        hexCodeDisplay.style.left = '20%';
        hexCodeDisplay.style.transform = 'translateX(-50%)';
        hexCodeDisplay.style.backgroundColor = '#fff';
        hexCodeDisplay.style.padding = '2px 10px';
        hexCodeDisplay.style.borderRadius = '4px';
        hexCodeDisplay.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.2)';
        hexCodeDisplay.style.display = 'none';
        hexCodeDisplay.style.textAlign = 'center';
        hexCodeDisplay.style.fontWeight = 'bold';
        hexCodeDisplay.style.color = '#333';
        hexCodeDisplay.style.fontSize = '10px';
        hexCodeDisplay.style.height = '10px';

        colorDiv.addEventListener('mouseenter', () => {
            hexCodeDisplay.style.display = 'block';
        });

        colorDiv.addEventListener('mouseleave', () => {
            hexCodeDisplay.style.display = 'none';
        });

        colorDiv.addEventListener('click', () => {
            navigator.clipboard.writeText(hexCode).then(() => {
                copiedMessage.textContent = `Copied: ${hexCode}`;
                copiedMessage.style.display = 'block';
                setTimeout(() => {
                    copiedMessage.style.display = 'none';
                }, 2000);
            });
        });

        if (isEditMode) {
            const deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = '&times;';
            deleteBtn.style.position = 'absolute';
            deleteBtn.style.top = '5px';
            deleteBtn.style.right = '5px';
            deleteBtn.style.width = '20px';
            deleteBtn.style.height = '20px';
            deleteBtn.style.borderRadius = '50%';
            deleteBtn.style.backgroundColor = '#ff4d4d';
            deleteBtn.style.color = '#fff';
            deleteBtn.style.border = 'none';
            deleteBtn.style.cursor = 'pointer';
            deleteBtn.style.fontSize = '14px';
            deleteBtn.style.zIndex = '1';

            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                paletteContainer.removeChild(colorDiv);
            });

            colorDiv.appendChild(deleteBtn);
        }

        colorDiv.appendChild(hexCodeDisplay);
        paletteContainer.appendChild(colorDiv);
    });

    paletteCard.style.display = 'block';
    paletteContainer.style.display = 'flex'; // Ensure the palette is visible
    const savedPalettesContainer = document.getElementById('saved-palettes-container');
    const paletteForm = document.getElementById('generate-palette-form');
    savedPalettesContainer.style.display = 'none'; // Hide saved palettes when new palette is displayed
    paletteForm.style.display = 'none';
}
