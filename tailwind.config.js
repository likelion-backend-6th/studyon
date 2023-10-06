/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    './templates/**/*.html'
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Pretendard-Regular', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        'base-black': "#373737",
      }
    },
  },
  plugins: [],
}

