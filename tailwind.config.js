/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-green': '#7AB857',
        'accent-yellow': '#FCD144',
        'card-pink': '#EAB2AB',
        'card-blue': '#93C4D8',
        'card-yellow': '#FCE3AB',
        'text-dark': '#333333',
        'link-blue': '#0074DB'
      },
      fontFamily: {
        'sans': ['ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif']
      },
      maxWidth: {
        'container': '1200px'
      }
    },
  },
  plugins: [],
}