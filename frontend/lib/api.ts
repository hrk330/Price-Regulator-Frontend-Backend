import axios from 'axios'
import { getApiUrl, getEnvironmentInfo } from './config'

// Flag to prevent infinite refresh loops
let isRefreshing = false

// Create axios instance with dynamic base URL
export const api = axios.create({
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Log environment info in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('🔧 API Configuration:', getEnvironmentInfo())
}

// Request interceptor to add auth token and update base URL dynamically
api.interceptors.request.use(
  (config) => {
    // Update base URL dynamically for each request
    const apiUrl = getApiUrl()
    config.baseURL = apiUrl
    
    // Debug logging for development
    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
      console.log('🌐 Making API request to:', apiUrl + config.url)
    }
    
    // Get access token from cookies and add to Authorization header
    const cookies = document.cookie.split(';')
    const accessTokenCookie = cookies.find(cookie => 
      cookie.trim().startsWith('access_token=')
    )
    
    if (accessTokenCookie && accessTokenCookie.trim().split('=')[1]) {
      const accessToken = accessTokenCookie.trim().split('=')[1]
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Only attempt refresh for 401 errors and not for refresh endpoint itself
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/refresh/') && !isRefreshing) {
      originalRequest._retry = true
      isRefreshing = true

      // Check if we have a refresh token before attempting refresh
      const cookies = document.cookie.split(';')
      const hasRefreshToken = cookies.some(cookie => 
        cookie.trim().startsWith('refresh_token=') && 
        cookie.trim().split('=')[1] && 
        cookie.trim().split('=')[1] !== ''
      )

      if (!hasRefreshToken) {
        // No refresh token, redirect to login immediately
        isRefreshing = false
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // Get refresh token from cookies
        const cookies = document.cookie.split(';')
        const refreshTokenCookie = cookies.find(cookie => 
          cookie.trim().startsWith('refresh_token=')
        )
        
        if (!refreshTokenCookie) {
          throw new Error('No refresh token found')
        }
        
        const refreshToken = refreshTokenCookie.trim().split('=')[1]
        
        // Try to refresh token
        await api.post('/auth/refresh/', {
          refresh_token: refreshToken,
          device_id: getDeviceId(),
        })

        // Retry original request
        isRefreshing = false
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, clear cookies and redirect to login
        isRefreshing = false
        document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
        document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Generate unique device ID
export function getDeviceId(): string {
  let deviceId = localStorage.getItem('device_id')
  if (!deviceId) {
    deviceId = 'device_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('device_id', deviceId)
  }
  return deviceId
}

// Auth API functions
export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', {
      email,
      password,
      device_id: getDeviceId(),
    })
    return response.data
  },

  logout: async () => {
    const response = await api.post('/auth/logout/', {
      device_id: getDeviceId(),
    })
    return response.data
  },

  refresh: async () => {
    // Get refresh token from cookies
    const cookies = document.cookie.split(';')
    const refreshTokenCookie = cookies.find(cookie => 
      cookie.trim().startsWith('refresh_token=')
    )
    
    if (!refreshTokenCookie) {
      throw new Error('No refresh token found')
    }
    
    const refreshToken = refreshTokenCookie.trim().split('=')[1]
    
    const response = await api.post('/auth/refresh/', {
      refresh_token: refreshToken,
      device_id: getDeviceId(),
    })
    return response.data
  },

  me: async () => {
    const response = await api.get('/auth/me/')
    return response.data
  },
}

// Products API functions
export const productsApi = {
  list: async (params?: any) => {
    const response = await api.get('/products/regulated-products/', { params })
    return response.data
  },

  create: async (data: any) => {
    const response = await api.post('/products/regulated-products/', data)
    return response.data
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/products/regulated-products/${id}/`, data)
    return response.data
  },

  delete: async (id: number) => {
    const response = await api.delete(`/products/regulated-products/${id}/`)
    return response.data
  },

  categories: async () => {
    const response = await api.get('/products/stats/')
    return response.data.category_stats || []
  },

  getRateLists: async () => {
    const response = await api.get('/products/rate-list-uploads/')
    return response.data
  },

  uploadRateList: async (formData: FormData) => {
    const response = await api.post('/products/upload-rate-list/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  downloadRateList: async (rateListId: string) => {
    const response = await api.get(`/products/rate-list-uploads/${rateListId}/download/`, {
      responseType: 'blob',
    })
    return response.data
  },

  deleteRateList: async (rateListId: string) => {
    const response = await api.delete(`/products/rate-list-uploads/${rateListId}/`)
    return response.data
  },
}

// Violations API functions
export const violationsApi = {
  list: async (params?: any) => {
    const response = await api.get('/violations/', { params })
    return response.data
  },

  get: async (id: number) => {
    const response = await api.get(`/violations/${id}/`)
    return response.data
  },

  confirm: async (id: number) => {
    const response = await api.post(`/violations/${id}/confirm/`)
    return response.data
  },

  dismiss: async (id: number) => {
    const response = await api.post(`/violations/${id}/dismiss/`)
    return response.data
  },

  stats: async () => {
    const response = await api.get('/violations/stats/')
    return response.data
  },
}

// Cases API functions
export const casesApi = {
  list: async (params?: any) => {
    const response = await api.get('/cases/', { params })
    return response.data
  },

  get: async (id: number) => {
    const response = await api.get(`/cases/${id}/`)
    return response.data
  },

  create: async (data: any) => {
    const response = await api.post('/cases/', data)
    return response.data
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/cases/${id}/`, data)
    return response.data
  },

  close: async (id: number, data: any) => {
    const response = await api.post(`/cases/${id}/close/`, data)
    return response.data
  },

  addNote: async (caseId: number, content: string) => {
    const response = await api.post(`/cases/${caseId}/notes/`, { content })
    return response.data
  },

  stats: async () => {
    const response = await api.get('/cases/stats/')
    return response.data
  },
}

// Scraping API functions
export const scrapingApi = {
  results: async (params?: any) => {
    const response = await api.get('/scraping/results/', { params })
    return response.data
  },

  jobs: async () => {
    const response = await api.get('/scraping/jobs/')
    return response.data
  },

  trigger: async (marketplace: string) => {
    const response = await api.post('/scraping/trigger/', { marketplace })
    return response.data
  },

  stats: async () => {
    const response = await api.get('/scraping/stats/')
    return response.data
  },

  getScrapedProducts: async () => {
    const response = await api.get('/scraping/results/')
    return response.data
  },

  getSearchLists: async () => {
    const response = await api.get('/scraping/product-lists/')
    return response.data
  },

  getScrapingWebsites: async () => {
    const response = await api.get('/scraping/websites/')
    return response.data
  },

  getScrapingLogs: async () => {
    const response = await api.get('/scraping/jobs/')
    return response.data
  },

  updateWebsiteStatus: async (websiteId: string, status: string) => {
    const response = await api.patch(`/scraping/websites/${websiteId}/`, { is_active: status === 'active' })
    return response.data
  },

  deleteWebsite: async (websiteId: string) => {
    const response = await api.delete(`/scraping/websites/${websiteId}/`)
    return response.data
  },

  updateSearchListStatus: async (listId: string, status: string) => {
    const response = await api.patch(`/scraping/product-lists/${listId}/`, { is_active: status === 'active' })
    return response.data
  },

  deleteSearchList: async (listId: string) => {
    const response = await api.delete(`/scraping/product-lists/${listId}/`)
    return response.data
  },
}

// Reports API functions
export const reportsApi = {
  summary: async (params?: any) => {
    const response = await api.get('/reports/summary/', { params })
    return response.data
  },

  export: async (type: string) => {
    const response = await api.get(`/reports/export/?type=${type}`, {
      responseType: 'blob',
    })
    return response.data
  },

  dashboardMetrics: async () => {
    const response = await api.get('/reports/dashboard-metrics/')
    return response.data
  },
}

// Users API functions
export const usersApi = {
  list: async (params?: { role?: string; page?: number; page_size?: number }) => {
    const response = await api.get('/users/', { params })
    return response.data
  },

  get: async (userId: string) => {
    const response = await api.get(`/users/${userId}/`)
    return response.data
  },

  create: async (userData: any) => {
    const response = await api.post('/users/', userData)
    return response.data
  },

  update: async (userId: string, userData: any) => {
    const response = await api.put(`/users/${userId}/`, userData)
    return response.data
  },

  delete: async (userId: string) => {
    const response = await api.delete(`/users/${userId}/`)
    return response.data
  },

  updateStatus: async (userId: string, status: string) => {
    const response = await api.patch(`/users/${userId}/status/`, { status })
    return response.data
  },
}

// Sessions API functions
export const sessionsApi = {
  list: async () => {
    const response = await api.get('/sessions/')
    return response.data
  },

  revoke: async (sessionId: string) => {
    const response = await api.delete(`/sessions/${sessionId}/revoke/`)
    return response.data
  },
}
