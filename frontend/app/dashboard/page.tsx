'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getCurrentUser, User, isAuthenticated } from '@/lib/auth'

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const router = useRouter()

  useEffect(() => {
    const checkUser = async () => {
      // First check if user has any authentication tokens
      if (!isAuthenticated()) {
        router.push('/login')
        return
      }

      const currentUser = await getCurrentUser()
      if (!currentUser) {
        router.push('/login')
        return
      }
      
      setUser(currentUser)
      
      // Redirect to role-specific dashboard
      if (currentUser.role === 'admin') {
        router.push('/dashboard/admin')
      } else if (currentUser.role === 'investigator') {
        router.push('/dashboard/investigator')
      } else if (currentUser.role === 'regulator') {
        router.push('/dashboard/regulator')
      }
    }

    checkUser()
  }, [router])

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return null
}
