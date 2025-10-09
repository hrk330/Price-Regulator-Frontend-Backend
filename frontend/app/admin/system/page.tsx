'use client'

import { useState } from 'react'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Save, RefreshCw, Database, Settings, Shield, Bell } from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function SystemPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [settings, setSettings] = useState({
    scrapingInterval: '24',
    violationThreshold: '10',
    emailNotifications: true,
    autoCaseCreation: true,
    backupFrequency: 'daily',
    logRetention: '30'
  })

  const handleSave = async () => {
    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Settings saved successfully')
    } catch (error) {
      toast.error('Failed to save settings')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestConnection = async () => {
    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Database connection successful')
    } catch (error) {
      toast.error('Database connection failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      {/* Page header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
          <p className="text-gray-600">
            Configure system parameters and preferences
          </p>
        </div>
        <button
          onClick={handleSave}
          disabled={isLoading}
          className="btn btn-primary flex items-center"
        >
          {isLoading ? (
            <LoadingSpinner size="sm" />
          ) : (
            <Save className="h-4 w-4 mr-2" />
          )}
          Save Settings
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scraping Settings */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <RefreshCw className="h-5 w-5 mr-2" />
              Scraping Configuration
            </h3>
          </div>
          <div className="card-body space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scraping Interval (hours)
              </label>
              <input
                type="number"
                value={settings.scrapingInterval}
                onChange={(e) => setSettings({...settings, scrapingInterval: e.target.value})}
                className="input"
                min="1"
                max="168"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Violation Threshold (%)
              </label>
              <input
                type="number"
                value={settings.violationThreshold}
                onChange={(e) => setSettings({...settings, violationThreshold: e.target.value})}
                className="input"
                min="1"
                max="100"
              />
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Bell className="h-5 w-5 mr-2" />
              Notifications
            </h3>
          </div>
          <div className="card-body space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Email Notifications
                </label>
                <p className="text-sm text-gray-500">
                  Send email alerts for violations and system events
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={(e) => setSettings({...settings, emailNotifications: e.target.checked})}
                className="toggle toggle-primary"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Auto Case Creation
                </label>
                <p className="text-sm text-gray-500">
                  Automatically create cases for confirmed violations
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.autoCaseCreation}
                onChange={(e) => setSettings({...settings, autoCaseCreation: e.target.checked})}
                className="toggle toggle-primary"
              />
            </div>
          </div>
        </div>

        {/* Database Settings */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Database className="h-5 w-5 mr-2" />
              Database Management
            </h3>
          </div>
          <div className="card-body space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Backup Frequency
              </label>
              <select
                value={settings.backupFrequency}
                onChange={(e) => setSettings({...settings, backupFrequency: e.target.value})}
                className="input"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Log Retention (days)
              </label>
              <input
                type="number"
                value={settings.logRetention}
                onChange={(e) => setSettings({...settings, logRetention: e.target.value})}
                className="input"
                min="7"
                max="365"
              />
            </div>
            <button
              onClick={handleTestConnection}
              disabled={isLoading}
              className="btn btn-outline flex items-center"
            >
              <Database className="h-4 w-4 mr-2" />
              Test Database Connection
            </button>
          </div>
        </div>

        {/* Security Settings */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Security & Access
            </h3>
          </div>
          <div className="card-body space-y-4">
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">Session Management</h4>
              <p className="text-sm text-gray-600">
                Configure user session timeouts and security policies
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">API Access</h4>
              <p className="text-sm text-gray-600">
                Manage API keys and access permissions
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">Audit Logs</h4>
              <p className="text-sm text-gray-600">
                View and manage system audit logs
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="card mt-6">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            System Status
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm font-medium text-gray-900">API Server</p>
              <p className="text-xs text-gray-500">Online</p>
            </div>
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm font-medium text-gray-900">Database</p>
              <p className="text-xs text-gray-500">Connected</p>
            </div>
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm font-medium text-gray-900">Scraping Service</p>
              <p className="text-xs text-gray-500">Active</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
