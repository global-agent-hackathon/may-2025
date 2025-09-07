// tailwind.config.ts
import type { Config } from "tailwindcss";

export default {
	darkMode: ["class"], // Keep for potential future dark mode
	content: [
		"./pages/**/*.{ts,tsx}",
		"./components/**/*.{ts,tsx}",
		"./app/**/*.{ts,tsx}",
		"./src/**/*.{ts,tsx}",
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px'
			}
		},
		extend: {
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))', // Will be our primary blue
				background: 'hsl(var(--background))', // Light cream/off-white
				foreground: 'hsl(var(--foreground))', // Dark gray for text
				primary: {
					DEFAULT: 'hsl(var(--primary))', // Blue
					foreground: 'hsl(var(--primary-foreground))' // White for text on blue
				},
				secondary: { // Can be a lighter gray or a complementary color
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				destructive: { // Keep this for error states
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				muted: { // For subtle text or backgrounds
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: { // Can be the primary blue or a variation
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				card: { // Cards will be white or very light
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
			},
			borderRadius: {
				lg: 'var(--radius)', // 0.5rem is good
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			keyframes: {
				'accordion-down': { from: { height: '0' }, to: { height: 'var(--radix-accordion-content-height)' } },
				'accordion-up': { from: { height: 'var(--radix-accordion-content-height)' }, to: { height: '0' } }
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out'
			},
      // Add a subtle grid background pattern
      backgroundImage: {
        'grid-pattern': "linear-gradient(to right, theme('colors.slate.100') 1px, transparent 1px), linear-gradient(to bottom, theme('colors.slate.100') 1px, transparent 1px)",
      },
      backgroundSize: {
        'grid-pattern': "20px 20px", // Adjust size of grid squares
      }
		}
	},
	plugins: [require("tailwindcss-animate")],
} satisfies Config;