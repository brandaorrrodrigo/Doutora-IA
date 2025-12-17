import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0b0e12",
        foreground: "#f4f4f5",
        primary: "#f4d28a",
        "primary-dark": "#d4b26a",
      },
    },
  },
  plugins: [],
};
export default config;
