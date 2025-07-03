// Google Fonts implementation for Geist Sans and Geist Mono
// This creates a CSS that imports the fonts from Google Fonts

// Create a style element for Google Fonts
const createGoogleFontStyle = () => {
  // Only create the style element once
  if (document.getElementById('geist-google-fonts')) return;

  const style = document.createElement('style');
  style.id = 'geist-google-fonts';
  style.textContent = `
    /* Geist Sans from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
    
    /* Geist Mono from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500&display=swap');
  `;
  document.head.appendChild(style);
};

// Initialize Google Fonts
if (typeof window !== 'undefined') {
  createGoogleFontStyle();
}

// Export font family constants
export const FONT_FAMILY = {
  sansSerif: 'Geist, sans-serif',
  mono: 'Geist Mono, monospace'
}; 