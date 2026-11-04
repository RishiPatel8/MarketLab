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
          bg: "#090604",            // Deep Black
          surface: "#130A06",       // Dark Brown
          card: "#1D0D06",          // Brown Black
          elevated: "#292725",      // Elevated Dark Charcoal
          hover: "#2C2928",         // Dark Charcoal
          border: "#403B36",        // Border
          "border-muted": "#512B19",// Deep Copper Muted Border
          pure: "#020101",          // Pure Black
          text: "#F5F2ED",          // Warm White
          soft: "#E8E1DA",          // Soft White
          secondary: "#A39A92",     // Secondary Grey
          muted: "#77716A",         // Muted Grey
        },
        gold: {
          DEFAULT: "#C47742",       // Primary Copper
          hover: "#D99560",         // Copper Hover / Light Copper
          strong: "#833512",        // Burnt Orange
          dim: "#5B2108",           // Copper Brown
          light: "#E6A776",         // Copper Highlight
          metallic: "#D28B55",      // Metallic Copper
          soft: "#D0A38F",          // Copper Light
          dark: "#512B19"           // Deep Copper
        },
        copper: {
          DEFAULT: "#C47742",       // Primary Copper
          hover: "#D99560",         // Light Copper
          strong: "#833512",        // Burnt Orange
          dim: "#5B2108",           // Copper Brown
          light: "#E6A776",         // Copper Highlight
          metallic: "#D28B55",      // Metallic Copper
          soft: "#D0A38F",          // Copper Light
          dark: "#512B19"           // Deep Copper
        },
        market: {
          positive: "#22C55E",      // Profit (Green)
          negative: "#EF4444",      // Loss (Red)
          warning: "#F59E0B",       // Hold / Warning (Amber)
          info: "#60A5FA",          // Information (Blue)
          benchmark: "#38BDF8"      // Benchmark (Sky Blue)
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      },
      borderRadius: {
        'button': '8px',
        'button-sm': '6px',
        'card': '10px',
        'card-lg': '12px',
        'xl': '8px',
        '2xl': '10px',
      }
    },
  },
  plugins: [],
}
