/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f7fc',
          100: '#e0eff9',
          200: '#b8daf2',
          300: '#8fc5eb',
          400: '#66b0e4',
          500: '#479be0',
          600: '#3a8ad0',
          700: '#2d6fa8',
          800: '#235680',
          900: '#1a3d5c',
          950: '#0f2438',
        },
      },
    },
  },
  plugins: [],
}
