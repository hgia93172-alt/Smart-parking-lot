/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: '#F5F5F5',
          sidebar: '#FFFFFF',
          panel: '#FFFFFF',
        },
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          DEFAULT: '#000000',
        },
        accent: {
          DEFAULT: '#7C3AED',
          hover: '#6D28D9',
        }
      },
      borderRadius: {
        'figma': '8px',
        'figma-lg': '12px',
      },
      boxShadow: {
        'figma': '0 0 0 1px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.05)',
        'figma-hover': '0 0 0 1px rgba(0,0,0,0.1), 0 4px 12px rgba(0,0,0,0.1)',
        'panel': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
