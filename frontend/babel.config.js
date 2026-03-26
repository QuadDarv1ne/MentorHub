/**
 * Babel configuration for MentorHub Frontend
 * Removes console.* statements in production builds
 */

const plugins = [
  // Remove console.* in production only
  [
    'transform-remove-console',
    {
      exclude: ['error', 'warn'], // Keep console.error and console.warn for error tracking
    },
  ],
]

module.exports = {
  presets: ['next/babel'],
  env: {
    production: {
      plugins,
    },
    development: {
      plugins: [], // Keep console.* in development
    },
  },
}
