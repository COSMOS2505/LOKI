/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        pixelBg: "#1a1a2e",
        pixelSurface: "#16213e",
        pixelCard: "#0f3460",
        pixelAccent: "#e94560",
        pixelAgent: "#4ade80",
        pixelGold: "#facc15",
      },
    },
  },
  plugins: [],
};