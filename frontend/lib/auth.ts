'use client'

import { authApi } from './api'
import toast from 'react-hot-toast'

export interface User {
  id: number
  email: string
  name: string
  role: 'admin' | 'investigator' | 'regulator'
  created_at: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}

// Auth context and hooks will be implemented in components
export const setAuthCookies = (accessToken: string, refreshToken: string) => {
  // Set cookies for development (without secure flag for localhost)
  const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  const secureFlag = isDevelopment ? '' : '; secure'
  
  document.cookie = `access_token=${accessToken}; path=/${secureFlag}; SameSite=Strict`
  document.cookie = `refresh_token=${refreshToken}; path=/${secureFlag}; SameSite=Strict`
}

export const clearAuthCookies = () => {
  document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
}

export const getAuthCookies = () => {
  const cookies = document.cookie.split(';')
  const authCookies: { [key: string]: string } = {}
  
  cookies.forEach(cookie => {
    const [name, value] = cookie.trim().split('=')
    if (name === 'access_token' || name === 'refresh_token') {
      authCookies[name] = value
    }
  })
  
  return authCookies
}

export const isAuthenticated = (): boolean => {
  const cookies = document.cookie.split(';')
  return cookies.some(cookie => 
    cookie.trim().startsWith('access_token=') && 
    cookie.trim().split('=')[1] && 
    cookie.trim().split('=')[1] !== ''
  )
}

export const login = async (email: string, password: string) => {
  try {
    const response = await authApi.login(email, password)
    
    // Set cookies
    setAuthCookies(response.access, response.refresh)
    
    toast.success('Login successful!')
    return response
  } catch (error: any) {
    const message = error.response?.data?.error || 'Login failed'
    toast.error(message)
    throw error
  }
}

export const logout = async () => {
  try {
    await authApi.logout()
    clearAuthCookies()
    toast.success('Logged out successfully')
  } catch (error) {
    // Even if logout fails on server, clear local cookies
    clearAuthCookies()
    toast.error('Logout failed, but you have been logged out locally')
  }
}

export const getCurrentUser = async (): Promise<User | null> => {
  try {
    // Check if we have an access token before making the API call
    const cookies = document.cookie.split(';')
    const hasAccessToken = cookies.some(cookie => 
      cookie.trim().startsWith('access_token=') && 
      cookie.trim().split('=')[1] && 
      cookie.trim().split('=')[1] !== ''
    )

    if (!hasAccessToken) {
      return null
    }

    const response = await authApi.me()
    return response
  } catch (error) {
    return null
  }
}

export const hasRole = (user: User | null, roles: string | string[]): boolean => {
  if (!user) return false
  
  const userRoles = Array.isArray(roles) ? roles : [roles]
  return userRoles.includes(user.role)
}

export const canAccess = (user: User | null, resource: string): boolean => {
  if (!user) return false
  
  switch (resource) {
    case 'admin':
      return user.role === 'admin'
    case 'investigator':
      return user.role === 'investigator' || user.role === 'admin'
    case 'regulator':
      return user.role === 'regulator' || user.role === 'admin'
    default:
      return false
  }
}
