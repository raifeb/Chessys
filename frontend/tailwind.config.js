/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gray: {
          50: '#f9fafb',
          100: '#eaedf1',
          200: '#e1e5eb',
          300: '#cbd2d9',
          400: '#9aa5b1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#243b53',
          900: '#102a43',
        },
        sidebar: {
          bg: '#141518',
          card: '#1b1c20',
          dark: '#0e0f11',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'clay-out': '6px 6px 14px #cfd4dc, -6px -6px 14px #ffffff',
        'clay-in': 'inset 3px 3px 6px #cfd4dc, inset -3px -3px 6px #ffffff',
        'clay-sm': '3px 3px 7px #cfd4dc, -3px -3px 7px #ffffff',
        'clay-in-sm': 'inset 2px 2px 4px #cfd4dc, inset -2px -2px 4px #ffffff',
        'clay-pill': '4px 4px 10px #d2d7df, -4px -4px 10px #ffffff',
        'dark-in': 'inset 2px 2px 6px rgba(0,0,0,0.6), inset -1px -1px 3px rgba(255,255,255,0.04)',
      }
    },
  },
  plugins: [],
}
