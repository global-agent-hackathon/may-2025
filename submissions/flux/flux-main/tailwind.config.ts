import type { Config } from "tailwindcss";

const config: Config = {
    content: [
		"./src/app/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/components/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
	],
	  
  prefix: "",
  theme: {
  	container: {
  		center: true,
  		padding: "2rem",
  		screens: {
  			"2xl": "1400px",
  		},
  	},
  	extend: {
  		colors: {
  			border: "hsl(var(--border))",
  			input: "hsl(var(--input))",
  			ring: "hsl(var(--ring))",
  			background: "hsl(var(--background))",
  			foreground: "hsl(var(--foreground))",
  			primary: {
  				DEFAULT: "hsl(var(--primary))",
  				foreground: "hsl(var(--primary-foreground))",
  			},
  			secondary: {
  				DEFAULT: "hsl(var(--secondary))",
  				foreground: "hsl(var(--secondary-foreground))",
  			},
  			destructive: {
  				DEFAULT: "hsl(var(--destructive))",
  				foreground: "hsl(var(--destructive-foreground))",
  			},
  			muted: {
  				DEFAULT: "hsl(var(--muted))",
  				foreground: "hsl(var(--muted-foreground))",
  			},
  			accent: {
  				DEFAULT: "hsl(var(--accent))",
  				foreground: "hsl(var(--accent-foreground))",
  			},
  			popover: {
  				DEFAULT: "hsl(var(--popover))",
  				foreground: "hsl(var(--popover-foreground))",
  			},
  			card: {
  				DEFAULT: "hsl(var(--card))",
  				foreground: "hsl(var(--card-foreground))",
  			},
  			sidebar: {
  				background: "#f8f8f8",
  				hover: "#f3f4f6",
  				active: "#1d4ed8",
  				text: "#111111",
  				muted: "#666666",
  			},
  			"primary-hover": "#1e40af",
  			"sidebar-bg": "#f9f9f9",
  			"sidebar-text": "#111111",
  			"sidebar-muted": "#666666",
  			"sidebar-hover": "#f3f4f6",
  		},
  		backgroundImage: {
  			'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
  			'hero-gradient': 'linear-gradient(135deg, #FFE1E1 0%, #E8F5E8 50%, #E1F1FF 100%)',
  		},
  		borderRadius: {
  			lg: "var(--radius)",
  			md: "calc(var(--radius) - 2px)",
  			sm: "calc(var(--radius) - 4px)",
  		},
  		boxShadow: {
  			sidebar: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
  		},
  		keyframes: {
  			"accordion-down": {
  				from: { height: "0" },
  				to: { height: "var(--radix-accordion-content-height)" },
  			},
  			"accordion-up": {
  				from: { height: "var(--radix-accordion-content-height)" },
  				to: { height: "0" },
  			},
  			moveVertical: {
  				"0%": {
  					transform: "translateY(-50%)",
  				},
  				"50%": {
  					transform: "translateY(50%)",
  				},
  				"100%": {
  					transform: "translateY(-50%)",
  				},
  			},
  			moveInCircle: {
  				"0%": {
  					transform: "rotate(0deg)",
  				},
  				"50%": {
  					transform: "rotate(180deg)",
  				},
  				"100%": {
  					transform: "rotate(360deg)",
  				},
  			},
  			moveHorizontal: {
  				"0%": {
  					transform: "translateX(-50%) translateY(-10%)",
  				},
  				"50%": {
  					transform: "translateX(50%) translateY(10%)",
  				},
  				"100%": {
  					transform: "translateX(-50%) translateY(-10%)",
  				},
  			},
  		},
  		animation: {
  			"accordion-down": "accordion-down 0.2s ease-out",
  			"accordion-up": "accordion-up 0.2s ease-out",
  			first: "moveVertical 30s ease infinite",
  			second: "moveInCircle 20s reverse infinite",
  			third: "moveInCircle 40s linear infinite",
  			fourth: "moveHorizontal 40s ease infinite",
  			fifth: "moveInCircle 20s ease infinite",
  		},
  	}
  },
  plugins: [
    require("tailwindcss-animate"),
    require("tailwind-scrollbar")
  ],
} satisfies Config;

export default config;
