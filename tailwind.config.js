// Used once to generate css/tailwind.css for the legal, science and blog pages (replaces the Tailwind CDN script).
// Regenerate: npx tailwindcss@3.4.17 -c tailwind.config.js -i css/tailwind.src.css -o css/tailwind.css --minify
module.exports = {
  content: ['./*.html', './blog/*.html'],
  theme: { extend: { colors: { brand: { 50: '#E9F1F7', 100: '#BDC5D4', 200: '#9AA7C1', 300: '#8587B7', 400: '#657FB1', 500: '#4677AC', 600: '#3a6090', 700: '#2e4a73', 800: '#223556', 900: '#162039' } } } },
}
