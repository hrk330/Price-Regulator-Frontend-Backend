'use client'

import { useQuery } from '@tanstack/react-query'
import { violationsApi, casesApi, scrapingApi, productsApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { AlertTriangle, FileText, Package, Search, Users, BarChart3, TrendingUp, Activity } from 'lucide-react'
import Link from 'next/link'

export default function AdminDashboard() {
  const { data: violationStats, isLoading: violationsLoading } = useQuery({
    queryKey: ['violation-stats'],
    queryFn: violationsApi.stats,
  })

  const { data: caseStats, isLoading: casesLoading } = useQuery({
    queryKey: ['case-stats'],
    queryFn: casesApi.stats,
  })

  const { data: scrapingStats, isLoading: scrapingLoading } = useQuery({
    queryKey: ['scraping-stats'],
    queryFn: scrapingApi.stats,
  })

  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ['products'],
    queryFn: () => productsApi.list({ page_size: 5 }),
  })

  if (violationsLoading || casesLoading || scrapingLoading || productsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const quickActions = [
    {
      title: 'Add Product',
      description: 'Add a new regulated product',
      href: '/admin/products/new',
      icon: Package,
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      title: 'Start Scraping',
      description: 'Trigger scraping jobs',
      href: '/admin/scraping',
      icon: Search,
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      title: 'Review Violations',
      description: 'Manage price violations',
      href: '/admin/violations',
      icon: AlertTriangle,
      color: 'bg-red-500 hover:bg-red-600'
    },
    {
      title: 'Create Case',
      description: 'Start new investigation',
      href: '/admin/cases/new',
      icon: FileText,
      color: 'bg-yellow-500 hover:bg-yellow-600'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Monitor and manage the price regulation system
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Package className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Products</p>
              <p className="text-2xl font-bold text-gray-900">
                {products?.count || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Violations</p>
              <p className="text-2xl font-bold text-gray-900">
                {violationStats?.pending_violations || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <FileText className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Open Cases</p>
              <p className="text-2xl font-bold text-gray-900">
                {caseStats?.open_cases || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Search className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Products Scraped</p>
              <p className="text-2xl font-bold text-gray-900">
                {scrapingStats?.total_products_scraped || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <Link
                  key={action.href}
                  href={action.href}
                  className={`${action.color} text-white rounded-lg p-4 transition-colors duration-200`}
                >
                  <div className="flex items-center">
                    <Icon className="h-6 w-6 mr-3" />
                    <div>
                      <p className="font-medium">{action.title}</p>
                      <p className="text-sm opacity-90">{action.description}</p>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      </div>

      {/* System Status and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Status */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">System Status</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Scraping Jobs</span>
                <span className="text-sm font-medium text-green-600">
                  {scrapingStats?.active_jobs_count || 0} Active
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Recent Activity</span>
                <span className="text-sm font-medium text-blue-600">
                  {scrapingStats?.recent_jobs_count || 0} Jobs (7 days)
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Marketplaces</span>
                <span className="text-sm font-medium text-purple-600">
                  {scrapingStats?.marketplace_stats?.length || 0} Active
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">API Status</span>
                <span className="text-sm font-medium text-green-600">Online</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg mr-3">
                  <Activity className="h-4 w-4 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">System Started</p>
                  <p className="text-xs text-gray-500">2 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg mr-3">
                  <Search className="h-4 w-4 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Scraping Job Completed</p>
                  <p className="text-xs text-gray-500">15 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center">
                <div className="p-2 bg-red-100 rounded-lg mr-3">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">New Violation Detected</p>
                  <p className="text-xs text-gray-500">1 hour ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
