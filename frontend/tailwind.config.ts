import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#E63946", // Anota AI Red style
          dark: "#C5303C",
          light: "#FF6B6B",
        },
        secondary: {
          DEFAULT: "#1D3557", // Deep Blue
          light: "#457B9D",
        },
        background: {
          DEFAULT: "#F3F4F6", // Light Gray
          dark: "#1F2937",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          hover: "#F9FAFB",
        }
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      }
    },
  },
  plugins: [],
};
export default config;
