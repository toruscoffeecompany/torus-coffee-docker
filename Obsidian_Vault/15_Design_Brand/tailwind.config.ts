import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: "#10172a",
        orbit: "#21314f",
        cream: "#fff8ea",
        stardust: "#f6c177",
        berry: "#d45b87",
        aurora: "#57c6b6",
        ink: "#182033",
      },
      fontFamily: {
        display: ["Georgia", "Cambria", "serif"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 18px 50px rgba(16, 23, 42, 0.14)",
      },
    },
  },
  plugins: [],
};

export default config;
