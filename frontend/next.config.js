/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === 'production'
        ? 'https://price-regulator-frontend-backend-production.up.railway.app/api'
        : 'http://localhost:8000/api'),
  },
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
      '@/*': path.resolve(__dirname, '*'),
    }

    // Disable fs for client bundles
    if (!isServer) {
      config.resolve.fallback = { fs: false }
    }

    // Ensure consistent resolution
    config.resolve.modules = [
      path.resolve(__dirname, 'node_modules'),
      'node_modules',
    ]

    return config
  },
}

module.exports = nextConfig
