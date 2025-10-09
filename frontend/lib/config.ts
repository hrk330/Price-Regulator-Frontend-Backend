/**
 * Environment configuration with automatic detection
 */

// Production API URL
const PRODUCTION_API_URL = 'https://price-regulator-frontend-backend-production.up.railway.app/api'

// Local development API URL
const LOCAL_API_URL = 'http://localhost:8000/api'

/**
 * Get the appropriate API URL based on environment
 */
export function getApiUrl(): string {
  // Check if we're in the browser
  if (typeof window === 'undefined') {
    // Server-side rendering - use environment variable or default to production
    return process.env.NEXT_PUBLIC_API_URL || PRODUCTION_API_URL
  }

  // Check if user has forced a specific API URL in localStorage
  const forcedApiUrl = localStorage.getItem('forced_api_url')
  if (forcedApiUrl) {
    console.log('🔧 Using forced API URL:', forcedApiUrl)
    return forcedApiUrl
  }

  // Check if user has set a preference to use production API even on localhost
  const useProductionApi = localStorage.getItem('use_production_api') === 'true'
  if (useProductionApi) {
    console.log('🔧 Using production API (forced):', PRODUCTION_API_URL)
    return PRODUCTION_API_URL
  }

  // Client-side - detect environment automatically
  const hostname = window.location.hostname
  
  // If running on localhost or 127.0.0.1, check if local backend is available
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.') || hostname.startsWith('10.')) {
    // Check if user has explicitly set to use local API
    const useLocalApi = localStorage.getItem('use_local_api') === 'true'
    if (useLocalApi) {
      console.log('🔧 User preference: using local API:', LOCAL_API_URL)
      return LOCAL_API_URL
    }
    
    // Default to production API for localhost frontend (since local backend might not be running)
    console.log('🔧 Auto-detected localhost frontend, defaulting to production API:', PRODUCTION_API_URL)
    return PRODUCTION_API_URL
  }
  
  // If running on production domain, use production API
  if (hostname.includes('railway.app') || hostname.includes('vercel.app') || hostname.includes('netlify.app')) {
    console.log('🔧 Auto-detected production domain, using production API:', PRODUCTION_API_URL)
    return PRODUCTION_API_URL
  }
  
  // For any other domain, check if NEXT_PUBLIC_API_URL is set
  if (process.env.NEXT_PUBLIC_API_URL) {
    console.log('🔧 Using environment variable API URL:', process.env.NEXT_PUBLIC_API_URL)
    return process.env.NEXT_PUBLIC_API_URL
  }
  
  // Default fallback to production
  console.log('🔧 Using default production API:', PRODUCTION_API_URL)
  return PRODUCTION_API_URL
}

/**
 * Check if we're running in development mode
 */
export function isDevelopment(): boolean {
  if (typeof window === 'undefined') {
    return process.env.NODE_ENV === 'development'
  }
  
  const hostname = window.location.hostname
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.') || hostname.startsWith('10.')
}

/**
 * Check if we're running in production mode
 */
export function isProduction(): boolean {
  return !isDevelopment()
}

/**
 * Force the API to use production URL even on localhost
 */
export function forceProductionApi(): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('use_production_api', 'true')
    // Clear any forced URL to use the production preference
    localStorage.removeItem('forced_api_url')
  }
}

/**
 * Force the API to use local URL
 */
export function forceLocalApi(): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('use_local_api', 'true')
    // Clear any forced URL to use the local preference
    localStorage.removeItem('forced_api_url')
    localStorage.removeItem('use_production_api')
  }
}

/**
 * Set a custom API URL
 */
export function setCustomApiUrl(url: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('forced_api_url', url)
    // Clear the production preference when setting custom URL
    localStorage.removeItem('use_production_api')
  }
}

/**
 * Reset API URL to automatic detection
 */
export function resetApiUrl(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('use_production_api')
    localStorage.removeItem('use_local_api')
    localStorage.removeItem('forced_api_url')
  }
}

/**
 * Get environment info for debugging
 */
export function getEnvironmentInfo() {
  return {
    apiUrl: getApiUrl(),
    isDevelopment: isDevelopment(),
    isProduction: isProduction(),
    hostname: typeof window !== 'undefined' ? window.location.hostname : 'server',
    nodeEnv: process.env.NODE_ENV,
    customApiUrl: process.env.NEXT_PUBLIC_API_URL,
    forcedApiUrl: typeof window !== 'undefined' ? localStorage.getItem('forced_api_url') : null,
    useProductionApi: typeof window !== 'undefined' ? localStorage.getItem('use_production_api') : null,
    useLocalApi: typeof window !== 'undefined' ? localStorage.getItem('use_local_api') : null,
  }
}
