/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',                  // Main index.html at vilcos/index.html
    './templates/**/*.html',         // Other HTML files in vilcos/templates/
    './templates/src/**/*.{js,ts,jsx,tsx}',   // JS/TS files in templates/src/
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}; 