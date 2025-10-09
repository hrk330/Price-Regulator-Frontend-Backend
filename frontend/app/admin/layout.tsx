'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getCurrentUser, User } from '@/lib/auth'
import { Header } from '@/components/layout/Header'
import AdminSidebar from '@/components/admin/AdminSidebar'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Menu } from 'lucide-react'

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await getCurrentUser()
        if (!currentUser) {
          router.push('/login')
          return
        }
        
        // Check if user is admin
        if (currentUser.role !== 'admin') {
          router.push('/dashboard')
          return
        }
        
        setUser(currentUser)
      } catch (error) {
        router.push('/login')
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="flex h-16 bg-white shadow-sm border-b border-gray-200">
        <div className="flex items-center px-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600"
          >
            <Menu className="h-6 w-6" />
          </button>
          <h1 className="ml-4 text-xl font-bold text-gray-900">Price Monitor</h1>
        </div>
        <div className="flex-1 flex justify-end">
          <Header user={user} />
        </div>
      </div>
      
      {/* Content */}
      <div className="flex h-[calc(100vh-4rem)]">
        <AdminSidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <div className="flex-1">
          <main className="h-full py-6 overflow-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
