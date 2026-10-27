/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          bg: "#09090B",
          surface: "#111114",
          card: "#18181B",
          elevated: "#202024",
          hover: "#27272A",
          border: "#27272A",
          "border-muted": "#3F3F46",
          text: "#FAFAF9",
          secondary: "#A1A1AA",
          muted: "#71717A",
        },
        gold: {
          DEFAULT: "#D4AF37",
          hover: "#E9CD70",
          dim: "#8C7323",
          light: "#F5E7B2",
          dark: "#3B300A"
        },
        market: {
          positive: "#22C55E",
          negative: "#F87171",
          warning: "#FBBF24",
          info: "#60A5FA",
          benchmark: "#3B82F6",
          secondary: "#A855F7"
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        'card': '16px',
        'card-lg': '20px'
      }
    },
  },
  plugins: [],
}
