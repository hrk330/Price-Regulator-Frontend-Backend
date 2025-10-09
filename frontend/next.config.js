/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    // Environment variables are now handled by the config.ts file
    // This allows for automatic environment detection
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  // Removed rewrites as they interfere with direct API calls
  // The API calls are now handled directly with automatic URL detection
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/:path*`,
  //     },
  //   ]
  // },
}

module.exports = nextConfig
