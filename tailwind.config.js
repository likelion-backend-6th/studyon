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
    }
  },
  plugins: [],
}

