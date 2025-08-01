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
        'link-blue': '#0074DB',
        // Cyberpunk Admin Colors
        'neon-pink': '#FF0080',
        'neon-orange': '#FF4500', 
        'neon-green': '#00FF41',
        'cyber-black': '#0A0A0A',
        'cyber-gray': '#1A1A1A',
        'cyber-gray-light': '#2A2A2A'
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