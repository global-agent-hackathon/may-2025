/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    fontFamily: {
      sans: ['Satoshi', 'sans-serif'],
      chat: ['Space Grotesk', 'sans-serif'], // Keep Space Grotesk for chat interface
    },
    extend: {
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.8s ease-in-out forwards',
        'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
        'infinite-scroll': 'infinite-scroll 30s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'infinite-scroll': {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(-50%)' },
        },
      },
      colors: {
        // Primary / Brand Colors
        purple: {
          light: '#C6A9E4', // Light Lavender
          DEFAULT: '#A484DE', // Soft Purple (main accent)
          dark: '#836AB2', // Dark Purple (for buttons, hover states)
        },
        // Neutrals & Support Colors
        'off-white': '#F6F3ED', // Off-White Background
        // Accent / Supporting Colors
        indigo: {
          DEFAULT: '#5767B4', // Indigo Blue
        },
        // Feedback & Status Colors
        success: '#28A745', // Success Green
        warning: '#FBBF24', // Warning Yellow
        error: '#EF4444',   // Error Red
        info: '#3B82F6',    // Info Blue
      },
      backgroundColor: {
        primary: '#F6F3ED', // Off-White Background
      },
      textColor: {
        primary: '#111827',   // Dark Text
        secondary: '#4B5563', // Secondary Text
        accent: '#6B7280',    // Icon/Accent Gray
      },
      borderColor: {
        DEFAULT: '#D1D5DB', // Gray Border
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
} 