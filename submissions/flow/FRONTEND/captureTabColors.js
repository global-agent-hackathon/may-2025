// Function to capture the visible tab and extract prominent colors
import { renderColorPalette } from './renderColorPalette.js';

const savedPalettesContainer = document.getElementById('savedPalettesContainer');
const generatePaletteForm = document.getElementById('generatePaletteForm');

// Function to calculate color difference using weighted RGB
function colorDifference(r1, g1, b1, r2, g2, b2) {
    const rMean = (r1 + r2) / 2;
    const rDiff = r1 - r2;
    const gDiff = g1 - g2;
    const bDiff = b1 - b2;

    // Weighted RGB color difference formula
    return Math.sqrt(
        (2 + rMean/256) * rDiff * rDiff +
        4 * gDiff * gDiff +
        (2 + (255-rMean)/256) * bDiff * bDiff
    );
}

// Function to find the most representative color in a cluster
function findRepresentativeColor(colors) {
    let minDistance = Infinity;
    let representativeColor = colors[0];

    for (const color of colors) {
        let totalDistance = 0;
        for (const otherColor of colors) {
            if (color !== otherColor) {
                const [r1, g1, b1] = color;
                const [r2, g2, b2] = otherColor;
                totalDistance += colorDifference(r1, g1, b1, r2, g2, b2);
            }
        }
        if (totalDistance < minDistance) {
            minDistance = totalDistance;
            representativeColor = color;
        }
    }
    return representativeColor;
}

export function captureTabColors() {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.tabs.captureVisibleTab(null, { format: 'png' }, function (dataUrl) {
            if (chrome.runtime.lastError) {
                console.error(chrome.runtime.lastError.message);
                return;
            }

            const img = new Image();
            img.src = dataUrl;

            img.onload = function () {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);

                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;

                // Sample colors with a grid to reduce processing
                const sampleStep = 4; // Sample every 4th pixel
                const colorSamples = [];

                for (let y = 0; y < canvas.height; y += sampleStep) {
                    for (let x = 0; x < canvas.width; x += sampleStep) {
                        const i = (y * canvas.width + x) * 4;
                        const r = data[i];
                        const g = data[i + 1];
                        const b = data[i + 2];
                        const a = data[i + 3];

                        // Skip transparent and very light colors
                        if (a < 128 || (r > 240 && g > 240 && b > 240)) {
                            continue;
                        }

                        colorSamples.push([r, g, b]);
                    }
                }

                // Simple color clustering
                const clusters = [];
                const colorThreshold = 30; // Threshold for considering colors similar

                for (const color of colorSamples) {
                    let foundCluster = false;
                    for (const cluster of clusters) {
                        const [r1, g1, b1] = color;
                        const [r2, g2, b2] = cluster[0];
                        if (colorDifference(r1, g1, b1, r2, g2, b2) < colorThreshold) {
                            cluster.push(color);
                            foundCluster = true;
                            break;
                        }
                    }
                    if (!foundCluster) {
                        clusters.push([color]);
                    }
                }

                // Sort clusters by size and get representative colors
                const prominentColors = clusters
                    .sort((a, b) => b.length - a.length)
                    .slice(0, 9)
                    .map(cluster => {
                        const [r, g, b] = findRepresentativeColor(cluster);
                        return rgbToHex(`rgb(${r},${g},${b})`);
                    });

                // Render the color palette using the reusable renderColorPalette function
                renderColorPalette(prominentColors);

                // Hide unnecessary elements and show palette form
                savedPalettesContainer.style.display = 'none';
                generatePaletteForm.style.display = 'none';
            };
        });
    });
}

// Function to convert RGB to Hex format
function rgbToHex(rgb) {
    const rgbValues = rgb.match(/\d+/g);
    const r = parseInt(rgbValues[0], 10);
    const g = parseInt(rgbValues[1], 10);
    const b = parseInt(rgbValues[2], 10);

    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`;
}
