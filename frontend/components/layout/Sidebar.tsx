'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { User } from '@/lib/auth'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Package,
  AlertTriangle,
  FileText,
  BarChart3,
  Settings,
  Menu,
  X,
  Users,
  Search,
  Download,
} from 'lucide-react'

interface SidebarProps {
  user: User
}

const navigation = {
  admin: [
    { name: 'Dashboard', href: '/dashboard/admin', icon: LayoutDashboard },
    { name: 'Products', href: '/dashboard/admin/products', icon: Package },
    { name: 'Scraping Jobs', href: '/dashboard/admin/scraping', icon: Search },
    { name: 'Violations', href: '/dashboard/admin/violations', icon: AlertTriangle },
    { name: 'Cases', href: '/dashboard/admin/cases', icon: FileText },
    { name: 'Reports', href: '/dashboard/admin/reports', icon: BarChart3 },
    { name: 'Sessions', href: '/dashboard/admin/sessions', icon: Users },
  ],
  investigator: [
    { name: 'Dashboard', href: '/dashboard/investigator', icon: LayoutDashboard },
    { name: 'Violations', href: '/dashboard/investigator/violations', icon: AlertTriangle },
    { name: 'Cases', href: '/dashboard/investigator/cases', icon: FileText },
  ],
  regulator: [
    { name: 'Dashboard', href: '/dashboard/regulator', icon: LayoutDashboard },
    { name: 'Reports', href: '/dashboard/regulator/reports', icon: BarChart3 },
    { name: 'Analytics', href: '/dashboard/regulator/analytics', icon: Download },
  ],
}

export function Sidebar({ user }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()
  const userNavigation = navigation[user.role as keyof typeof navigation] || []

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 rounded-md bg-white shadow-md"
        >
          {isOpen ? (
            <X className="h-6 w-6 text-gray-600" />
          ) : (
            <Menu className="h-6 w-6 text-gray-600" />
          )}
        </button>
      </div>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black bg-opacity-50"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed top-16 left-0 bottom-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* User info */}
          <div className="px-4 py-4 border-b border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600">
                    {user.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">{user.name}</p>
                <p className="text-xs text-gray-500 capitalize">{user.role}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1">
            {userNavigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  <item.icon
                    className={cn(
                      'mr-3 h-5 w-5 flex-shrink-0',
                      isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="px-4 py-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Price Regulation Monitoring System
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
