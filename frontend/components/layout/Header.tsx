'use client'

import { useState } from 'react'
import { User, logout } from '@/lib/auth'
import { useRouter, usePathname } from 'next/navigation'
import { Bell, LogOut, User as UserIcon } from 'lucide-react'

interface HeaderProps {
  user: User
}

export function Header({ user }: HeaderProps) {
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  // Get page title based on current route
  const getPageTitle = () => {
    if (pathname.includes('/products')) return 'Products'
    if (pathname.includes('/violations')) return 'Violations'
    if (pathname.includes('/cases')) return 'Cases'
    if (pathname.includes('/reports')) return 'Reports'
    if (pathname.includes('/sessions')) return 'Sessions'
    if (pathname.includes('/scraping')) return 'Scraping Jobs'
    if (pathname.includes('/analytics')) return 'Analytics'
    
    // Default dashboard titles
    if (user.role === 'admin') return 'Admin Dashboard'
    if (user.role === 'investigator') return 'Investigator Dashboard'
    if (user.role === 'regulator') return 'Regulator Dashboard'
    
    return 'Dashboard'
  }

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      // Error is handled in logout function
    }
  }

  return (
    <header className="h-16 flex-shrink-0">
      <div className="h-full flex items-center px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center w-full">
          {/* Page title */}
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              {getPageTitle()}
            </h1>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="p-2 text-gray-400 hover:text-gray-500 relative">
              <Bell className="h-6 w-6" />
              <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Profile dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50"
              >
                <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600">
                    {user.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">{user.name}</p>
                  <p className="text-xs text-gray-500 capitalize">{user.role}</p>
                </div>
              </button>

              {/* Dropdown menu */}
              {isProfileOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user.name}</p>
                    <p className="text-xs text-gray-500">{user.email}</p>
                  </div>
                  
                  <button
                    onClick={() => {
                      setIsProfileOpen(false)
                      // Add profile page navigation here
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <UserIcon className="h-4 w-4 mr-3" />
                    Profile
                  </button>
                  
                  <button
                    onClick={handleLogout}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <LogOut className="h-4 w-4 mr-3" />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Click outside to close dropdown */}
      {isProfileOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsProfileOpen(false)}
        />
      )}
    </header>
  )
}
