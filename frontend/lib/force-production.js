// Quick script to force production API
// Run this in browser console: 
// fetch('/lib/force-production.js').then(r => r.text()).then(eval)

// Clear all API preferences
localStorage.removeItem('use_production_api')
localStorage.removeItem('use_local_api') 
localStorage.removeItem('forced_api_url')

// Force production API
localStorage.setItem('use_production_api', 'true')

console.log('✅ Forced to use Production API')
console.log('🔄 Reload the page to apply changes')

// Show current config
const config = {
  apiUrl: localStorage.getItem('use_production_api') === 'true' ? 'https://price-regulator-frontend-backend-production.up.railway.app/api' : 'http://localhost:8000/api',
  useProductionApi: localStorage.getItem('use_production_api'),
  useLocalApi: localStorage.getItem('use_local_api'),
  forcedApiUrl: localStorage.getItem('forced_api_url')
}

console.log('🔧 Current config:', config)
