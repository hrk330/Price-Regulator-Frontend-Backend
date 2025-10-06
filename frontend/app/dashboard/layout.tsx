'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getCurrentUser, User } from '@/lib/auth'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await getCurrentUser()
        if (!currentUser) {
          router.push('/login')
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
      {/* Unified header row */}
      <div className="flex h-16">
        {/* Sidebar header */}
        <div className="w-64 bg-primary-600 flex items-center justify-center">
          <h1 className="text-xl font-bold text-white">Price Monitor</h1>
        </div>
        {/* Main header */}
        <div className="flex-1 bg-white shadow-sm border-b border-gray-200">
          <Header user={user} />
        </div>
      </div>
      
      {/* Content row */}
      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar user={user} />
        <div className="flex-1 lg:ml-64">
          <main className="h-full py-4 overflow-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
