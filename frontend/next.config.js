/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  // ✅ Automatically select correct API URL
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === 'production'
        ? 'https://price-regulator-frontend-backend-production.up.railway.app/api'
        : 'http://localhost:8000/api'),
  },

  webpack: (config, { isServer }) => {
    // ✅ Alias for absolute imports
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    }

    // ✅ Prevent "fs" issue on client side
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      }
    }

    return config
  },
}

module.exports = nextConfig
