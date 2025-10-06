'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/lib/auth'

export default function HomePage() {
  const router = useRouter()

  useEffect(() => {
    // Check if user is logged in
    if (isAuthenticated()) {
      // User is logged in, redirect to dashboard
      router.push('/dashboard')
    } else {
      // User is not logged in, redirect to login
      router.push('/login')
    }
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  )
}
