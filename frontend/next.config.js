const { withSentryConfig } = require('@sentry/nextjs')
const withNextIntl = require('next-intl/plugin')('./i18n.ts')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',

  poweredByHeader: false,
  compress: true,

  // Performance optimizations for Lighthouse
  generateEtags: true,
  httpAgentOptions: {
    keepAlive: true,
  },

  eslint: {
    ignoreDuringBuilds: true,
  },

  // Security headers for Lighthouse best-practices
  headers: async () => [
    {
      source: '/:path*',
      headers: [
        {
          key: 'X-DNS-Prefetch-Control',
          value: 'on',
        },
        {
          key: 'Strict-Transport-Security',
          value: 'max-age=63072000; includeSubDomains; preload',
        },
        {
          key: 'X-Frame-Options',
          value: 'SAMEORIGIN',
        },
        {
          key: 'X-Content-Type-Options',
          value: 'nosniff',
        },
        {
          key: 'X-XSS-Protection',
          value: '1; mode=block',
        },
        {
          key: 'Referrer-Policy',
          value: 'origin-when-cross-origin',
        },
      ],
    },
  ],

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.stepik.net',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    // Lighthouse optimizations
    minimumCacheTTL: 60,
    contentDispositionType: 'inline',
  },

  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
    optimizeCss: true,
    optimizePackageImports: ['lucide-react'],
    // Additional performance features
    scrollRestoration: true,
    // Reduce JavaScript bundle
    webpackBuildWorker: true,
  },

  webpack: (config, {isServer}) => {
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            commons: {
              name: 'commons',
              chunks: 'all',
              minChunks: 2,
            },
            lib: {
              test: /[\\/]node_modules[\\/]/,
              name: 'lib',
              chunks: 'all',
              priority: 10,
            },
            lucide: {
              test: /[\\/]node_modules[\\/](lucide-react)[\\/]/,
              name: 'lucide',
              chunks: 'all',
              priority: 20,
            },
            // Separate React and Next.js core
            react: {
              test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/,
              name: 'react',
              chunks: 'all',
              priority: 50,
            },
            next: {
              test: /[\\/]node_modules[\\/](next)[\\/]/,
              name: 'next',
              chunks: 'all',
              priority: 60,
            },
          },
        },
        // Minimize CSS
        minimize: true,
      }
    }
    return config
  },
}

const sentryWebpackPluginOptions = {
  silent: true,
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  authToken: process.env.SENTRY_AUTH_TOKEN,
}

module.exports = withSentryConfig(
  withNextIntl(nextConfig),
  sentryWebpackPluginOptions
)