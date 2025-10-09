/**
 * API Control Utilities
 * These functions can be called from the browser console to control the API URL
 */

import { forceProductionApi, forceLocalApi, resetApiUrl, getEnvironmentInfo } from './config'

// Make these functions available globally for console access
if (typeof window !== 'undefined') {
  (window as any).apiControls = {
    useProduction: () => {
      forceProductionApi()
      console.log('✅ Forced to use Production API')
      console.log('Current config:', getEnvironmentInfo())
      console.log('🔄 Reload the page to apply changes')
    },
    
    useLocal: () => {
      forceLocalApi()
      console.log('✅ Forced to use Local API')
      console.log('Current config:', getEnvironmentInfo())
      console.log('🔄 Reload the page to apply changes')
    },
    
    reset: () => {
      resetApiUrl()
      console.log('✅ Reset to automatic detection')
      console.log('Current config:', getEnvironmentInfo())
      console.log('🔄 Reload the page to apply changes')
    },
    
    info: () => {
      console.log('🔧 Current API Configuration:', getEnvironmentInfo())
    },
    
    help: () => {
      console.log(`
🚀 API Controls Available:
  apiControls.useProduction() - Force production API
  apiControls.useLocal()      - Force local API  
  apiControls.reset()         - Reset to auto-detect
  apiControls.info()          - Show current config
  apiControls.help()          - Show this help
      `)
    }
  }
  
  // Show help on load
  console.log('🚀 API Controls loaded! Type apiControls.help() for available commands')
}
