// svgGenerator.js

export function generateVector(svgCode) {
    const svgContainer = document.getElementById('svgContainer');
    svgContainer.style.display = 'block';
    svgContainer.innerHTML = svgCode;

    // Show buttons for interacting with the SVG code
    document.getElementById('showCodeButton').style.display = 'block';
    document.getElementById('copyCodeButton').style.display = 'block';
    document.getElementById('saveSvgButton').style.display = 'block';
    const downloaded = document.getElementById('downloaded-message');
    const copied = document.getElementById('copiedSvg-message');

    // Handle the "Show SVG Code" button click
    document.getElementById('showCodeButton').onclick = () => {
        const svgCodeDisplay = document.getElementById('svgCodeDisplay');
        svgCodeDisplay.textContent = svgCode;
        svgCodeDisplay.style.display = svgCodeDisplay.style.display === 'none' ? 'block' : 'none'; // Toggle visibility
    };

    // Handle the "Copy SVG Code" button click
    document.getElementById('copyCodeButton').onclick = () => {
        navigator.clipboard.writeText(svgCode)
            .then(() => {
                copied.style.display = 'block';
                setTimeout(() => {
                    copied.style.display = 'none';
                }, 2000);
            })
            .catch(err => {
                console.error('Error copying SVG code:', err);
                alert('Failed to copy SVG code.');
            });
    };

    // Handle the "Save as SVG File" button click
    document.getElementById('saveSvgButton').onclick = () => {
        const blob = new Blob([svgCode], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'icon.svg'; // Name of the saved file
        document.body.appendChild(a);
        a.click(); // Trigger the download
        document.body.removeChild(a);
        URL.revokeObjectURL(url); // Clean up the URL object
        downloaded.style.display = 'block';
        setTimeout(() => {
            downloaded.style.display = 'none';
        }, 4000);
    };
}

