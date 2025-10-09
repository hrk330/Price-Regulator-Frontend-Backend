/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  webpack: (config, { isServer, buildId, dev, defaultLoaders, webpack }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      }
    }
    
    // More explicit path resolution
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(process.cwd()),
      '@/lib': path.resolve(process.cwd(), 'lib'),
      '@/components': path.resolve(process.cwd(), 'components'),
      '@/app': path.resolve(process.cwd(), 'app'),
    }
    
    // Ensure proper module resolution
    config.resolve.modules = [
      path.resolve(process.cwd(), 'node_modules'),
      'node_modules'
    ]
    
    return config
  },
}

module.exports = nextConfig
