import { initializeTab2 } from './tab2.js';
import { initializeTab3 } from './tab3.js';
import { initializeTab4 } from './tab4.js';
import { initializeTab6 } from './tab6.js';
import { initializeTab7 } from './tab7.js';

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all tabs
    initializeTab2();
    initializeTab3();
    initializeTab4();
    initializeTab6();
    initializeTab7();

    // Function to switch between main tabs
    function switchTab(tabNumber) {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => button.classList.remove('active'));
        tabContents.forEach(content => content.style.display = 'none');

        document.getElementById(`tab${tabNumber}Btn`).classList.add('active');
        document.getElementById(`tab${tabNumber}`).style.display = 'block';
    }

    // Function to switch between Font and Vector modes
    function switchMode(mode) {
        // Hide all form and output elements first
        const elementsToHide = [
            'generate-font-form',
            'generate-icon-form',
            'successIcon',
            'loadingMessage',
            'loading-message3',
            'loading-message4',
            'analysisOutput',
            'analysisOutput1',
            'svgContainer',
            'showCodeButton',
            'copyCodeButton',
            'saveSvgButton',
            'svgCodeDisplay'
        ];

        elementsToHide.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.display = 'none';
            }
        });

        // Show elements based on selected mode
        if (mode === 'font') {
            const fontForm = document.getElementById('generate-font-form');
            const fontOutput = document.getElementById('analysisOutput1');
            const fontCardsContainer = document.querySelector('#tab3 > div[style*="display: flex"]');

            if (fontForm) {
                fontForm.style.display = 'block';
            }
            if (fontOutput && fontOutput.textContent.trim() !== '') {
                fontOutput.style.display = 'block';
            }
            if (fontCardsContainer) {
                fontCardsContainer.style.display = 'flex';
            }
        } else if (mode === 'vector') {
            const vectorForm = document.getElementById('generate-icon-form');
            if (vectorForm) {
                vectorForm.style.display = 'block';
            }
        }
    }

    // Event listeners for tab buttons
    document.getElementById('tab1Btn').addEventListener('click', () => switchTab(1));
    document.getElementById('tab2Btn').addEventListener('click', () => switchTab(2));
    document.getElementById('tab3Btn').addEventListener('click', () => {
        switchTab(3);
        // Don't show any form by default
        switchMode('none');
    });
    document.getElementById('tab5Btn').addEventListener('click', () => switchTab(5));
    document.getElementById('tab6Btn').addEventListener('click', () => switchTab(6));
    document.getElementById('tab7Btn').addEventListener('click', () => switchTab(7));

    // Add event listeners for Font and Vector buttons
    const fontBtn = document.getElementById('fontBtn');
    const vectorBtn = document.getElementById('VectorBtn');

    if (fontBtn) {
        fontBtn.addEventListener('click', () => switchMode('font'));
    }
    if (vectorBtn) {
        vectorBtn.addEventListener('click', () => switchMode('vector'));
    }

    // Set Tab 1 as default
    window.onload = () => switchTab(1);
});

