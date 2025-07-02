export function updatePalette(isEditMode) {

    const paletteContainer = document.getElementById('palette-container');

    const colorDivs = document.querySelectorAll('.color-box');
    colorDivs.forEach(colorDiv => {
        const deleteBtn = colorDiv.querySelector('button');
        if (isEditMode) {
            if (!deleteBtn) {
                const newDeleteBtn = document.createElement('button');
                newDeleteBtn.innerHTML = '&times;'; // Using '×' as a delete icon
                newDeleteBtn.style.position = 'absolute';
                newDeleteBtn.style.bottom = '5px'; // Changed to 'top' for better visibility
                newDeleteBtn.style.right = '5px'; // Changed to 'right' for better visibility
                newDeleteBtn.style.width = '25px'; // Increased size for easier clickability
                newDeleteBtn.style.height = '25px'; // Increased size for easier clickability
                newDeleteBtn.style.borderRadius = '50%'; // Make it circular
                newDeleteBtn.style.backgroundColor = 'transparent'; // Make background transparent
                newDeleteBtn.style.color = '#ff4d4d'; // Color of the '×'
                newDeleteBtn.style.border = 'none'; // No border
                newDeleteBtn.style.cursor = 'pointer'; // Pointer cursor on hover
                newDeleteBtn.style.fontSize = '20px'; // Font size of the '×'
                newDeleteBtn.style.lineHeight = '20px'; // Line height to center the text
                newDeleteBtn.style.textAlign = 'center'; // Center the text
                newDeleteBtn.style.zIndex = '1'; // Ensure the button is on top of the color box
                newDeleteBtn.style.opacity = '1'; // Fully visible '×' icon
                newDeleteBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    paletteContainer.removeChild(colorDiv);
                });
                colorDiv.appendChild(newDeleteBtn);

            }
        } else if (deleteBtn) {
            colorDiv.removeChild(deleteBtn);
        }
    });
}
