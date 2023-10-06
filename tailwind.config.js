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
                "real-blue": "#0000ff",
                "wanted-blue": "#6288EF",
                "wanted-indigo": "#4059E1",
                "wanted-green": "#89DABF",
                "wanted-cyan": "#89DADF"
            }
        },
    },
    plugins: [],
}

