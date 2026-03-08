"use client"

import React from 'react'
import { useTheme } from './ThemeProvider'
import { Moon, Sun, Monitor } from 'lucide-react'

export default function ThemeToggle() {
  const { theme, setTheme, actualTheme } = useTheme()

  return (
    <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
      <button
        onClick={() => setTheme('light')}
        className={`p-2 rounded-md transition-all ${
          theme === 'light'
            ? 'bg-white dark:bg-gray-700 shadow-sm text-amber-600'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
        }`}
        aria-label="Switch to light theme"
        title="Light mode"
      >
        <Sun className="h-5 w-5" />
      </button>

      <button
        onClick={() => setTheme('dark')}
        className={`p-2 rounded-md transition-all ${
          theme === 'dark'
            ? 'bg-white dark:bg-gray-700 shadow-sm text-indigo-600'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
        }`}
        aria-label="Switch to dark theme"
        title="Dark mode"
      >
        <Moon className="h-5 w-5" />
      </button>

      <button
        onClick={() => setTheme('system')}
        className={`p-2 rounded-md transition-all ${
          theme === 'system'
            ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
        }`}
        aria-label="Use system theme"
        title="System default"
      >
        <Monitor className="h-5 w-5" />
      </button>
    </div>
  )
}
