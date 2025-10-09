'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Package, 
  Search, 
  AlertTriangle, 
  FileText, 
  Users, 
  Settings,
  BarChart3,
  Upload,
  Database,
  Activity
} from 'lucide-react'

const adminMenuItems = [
  {
    title: 'Dashboard',
    href: '/admin',
    icon: BarChart3,
    description: 'Overview and statistics'
  },
  {
    title: 'Products',
    href: '/admin/products',
    icon: Package,
    description: 'Manage regulated products',
    subItems: [
      { title: 'All Products', href: '/admin/products' },
      { title: 'Rate List Uploads', href: '/admin/products/rate-lists' },
      { title: 'Add Product', href: '/admin/products/new' }
    ]
  },
  {
    title: 'Scraping',
    href: '/admin/scraping',
    icon: Search,
    description: 'Manage scraping operations',
    subItems: [
      { title: 'Scraping Jobs', href: '/admin/scraping' },
      { title: 'Scraped Products', href: '/admin/scraping/products' },
      { title: 'Product Search Lists', href: '/admin/scraping/search-lists' },
      { title: 'Scraping Websites', href: '/admin/scraping/websites' },
      { title: 'Job Logs', href: '/admin/scraping/logs' }
    ]
  },
  {
    title: 'Violations',
    href: '/admin/violations',
    icon: AlertTriangle,
    description: 'Review price violations',
    subItems: [
      { title: 'All Violations', href: '/admin/violations' },
      { title: 'Pending Review', href: '/admin/violations?status=pending' },
      { title: 'Confirmed', href: '/admin/violations?status=confirmed' },
      { title: 'Dismissed', href: '/admin/violations?status=dismissed' }
    ]
  },
  {
    title: 'Cases',
    href: '/admin/cases',
    icon: FileText,
    description: 'Manage investigation cases',
    subItems: [
      { title: 'All Cases', href: '/admin/cases' },
      { title: 'Open Cases', href: '/admin/cases?status=open' },
      { title: 'Investigating', href: '/admin/cases?status=investigating' },
      { title: 'Closed Cases', href: '/admin/cases?status=closed' },
      { title: 'Create Case', href: '/admin/cases/new' }
    ]
  },
  {
    title: 'Users',
    href: '/admin/users',
    icon: Users,
    description: 'Manage system users',
    subItems: [
      { title: 'All Users', href: '/admin/users' },
      { title: 'Admins', href: '/admin/users?role=admin' },
      { title: 'Investigators', href: '/admin/users?role=investigator' },
      { title: 'Regulators', href: '/admin/users?role=regulator' },
      { title: 'Add User', href: '/admin/users/new' }
    ]
  },
  {
    title: 'Reports',
    href: '/admin/reports',
    icon: Activity,
    description: 'Generate reports and analytics',
    subItems: [
      { title: 'Dashboard Metrics', href: '/admin/reports/metrics' },
      { title: 'Violation Reports', href: '/admin/reports/violations' },
      { title: 'Case Reports', href: '/admin/reports/cases' },
      { title: 'Export Data', href: '/admin/reports/export' }
    ]
  },
  {
    title: 'System',
    href: '/admin/system',
    icon: Settings,
    description: 'System configuration',
    subItems: [
      { title: 'Settings', href: '/admin/system/settings' },
      { title: 'Logs', href: '/admin/system/logs' },
      { title: 'Backup', href: '/admin/system/backup' },
      { title: 'Maintenance', href: '/admin/system/maintenance' }
    ]
  }
]

interface AdminSidebarProps {
  isOpen: boolean
  onClose: () => void
}

export default function AdminSidebar({ isOpen, onClose }: AdminSidebarProps) {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/admin') {
      return pathname === href
    }
    return pathname.startsWith(href)
  }

  const isSubItemActive = (href: string) => {
    return pathname === href
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-80 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        lg:translate-x-0 lg:relative lg:inset-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-xl font-bold text-gray-900">Navigation</h2>
            <button
              onClick={onClose}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {adminMenuItems.map((item) => {
                const Icon = item.icon
                const active = isActive(item.href)
                
                return (
                  <div key={item.href}>
                    <Link
                      href={item.href}
                      className={`
                        flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors
                        ${active 
                          ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700' 
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                        }
                      `}
                    >
                      <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
                      <div className="flex-1">
                        <div>{item.title}</div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {item.description}
                        </div>
                      </div>
                    </Link>

                    {/* Sub-items */}
                    {item.subItems && active && (
                      <div className="ml-8 mt-2 space-y-1">
                        {item.subItems.map((subItem) => (
                          <Link
                            key={subItem.href}
                            href={subItem.href}
                            className={`
                              block px-4 py-2 text-sm rounded-md transition-colors
                              ${isSubItemActive(subItem.href)
                                ? 'bg-blue-100 text-blue-700 font-medium'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                              }
                            `}
                          >
                            {subItem.title}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t">
            <div className="text-xs text-gray-500 text-center">
              Price Regulation Monitoring System
              <br />
              Admin Panel v1.0
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
