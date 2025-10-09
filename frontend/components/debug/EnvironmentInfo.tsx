'use client'

import { useEffect, useState } from 'react'
import { getEnvironmentInfo, forceProductionApi, forceLocalApi, resetApiUrl } from '@/lib/config'

interface EnvironmentInfoProps {
  showInProduction?: boolean
}

export default function EnvironmentInfo({ showInProduction = false }: EnvironmentInfoProps) {
  const [envInfo, setEnvInfo] = useState<any>(null)
  const [isVisible, setIsVisible] = useState(false)

  const refreshEnvInfo = () => {
    setEnvInfo(getEnvironmentInfo())
  }

  useEffect(() => {
    refreshEnvInfo()
  }, [])

  const handleForceProduction = () => {
    forceProductionApi()
    refreshEnvInfo()
    // Reload the page to apply the new API URL
    window.location.reload()
  }

  const handleForceLocal = () => {
    forceLocalApi()
    refreshEnvInfo()
    // Reload the page to apply the new API URL
    window.location.reload()
  }

  const handleReset = () => {
    resetApiUrl()
    refreshEnvInfo()
    // Reload the page to apply the new API URL
    window.location.reload()
  }

  // Only show in development or if explicitly requested
  if (!showInProduction && process.env.NODE_ENV === 'production') {
    return null
  }

  if (!envInfo) {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="bg-blue-500 text-white px-3 py-1 rounded text-xs hover:bg-blue-600 transition-colors"
      >
        {isVisible ? 'Hide' : 'Show'} Env Info
      </button>
      
      {isVisible && (
        <div className="absolute bottom-8 right-0 bg-gray-900 text-white p-3 rounded-lg shadow-lg text-xs max-w-sm">
          <div className="font-bold mb-2">🔧 Environment Info</div>
          <div className="space-y-1 mb-3">
            <div><strong>API URL:</strong> {envInfo.apiUrl}</div>
            <div><strong>Environment:</strong> {envInfo.isDevelopment ? 'Development' : 'Production'}</div>
            <div><strong>Hostname:</strong> {envInfo.hostname}</div>
            <div><strong>Node Env:</strong> {envInfo.nodeEnv}</div>
            {envInfo.customApiUrl && (
              <div><strong>Custom API URL:</strong> {envInfo.customApiUrl}</div>
            )}
            {envInfo.forcedApiUrl && (
              <div><strong>Forced API URL:</strong> {envInfo.forcedApiUrl}</div>
            )}
            {envInfo.useProductionApi && (
              <div><strong>Force Production:</strong> {envInfo.useProductionApi}</div>
            )}
            {envInfo.useLocalApi && (
              <div><strong>Force Local:</strong> {envInfo.useLocalApi}</div>
            )}
          </div>
          
          <div className="border-t border-gray-600 pt-2">
            <div className="font-bold mb-2">API Controls:</div>
            <div className="space-y-1">
              <button
                onClick={handleForceProduction}
                className="w-full bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-xs transition-colors"
              >
                Use Production API
              </button>
              <button
                onClick={handleForceLocal}
                className="w-full bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs transition-colors"
              >
                Use Local API
              </button>
              <button
                onClick={handleReset}
                className="w-full bg-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-xs transition-colors"
              >
                Auto Detect
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
