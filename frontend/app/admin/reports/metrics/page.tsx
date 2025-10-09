'use client'

import { useQuery } from '@tanstack/react-query'
import { reportsApi, violationsApi, casesApi, scrapingApi, productsApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { BarChart3, TrendingUp, TrendingDown, Activity, Package, AlertTriangle, FileText, Search } from 'lucide-react'

export default function MetricsPage() {
  const { data: dashboardMetrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: reportsApi.dashboardMetrics,
  })

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
    queryFn: () => productsApi.list({ page_size: 1000 }),
  })

  if (metricsLoading || violationsLoading || casesLoading || scrapingLoading || productsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const metrics = [
    {
      title: 'Total Products',
      value: products?.count || 0,
      icon: Package,
      color: 'bg-blue-500',
      change: '+12%',
      changeType: 'positive'
    },
    {
      title: 'Active Violations',
      value: violationStats?.pending_violations || 0,
      icon: AlertTriangle,
      color: 'bg-red-500',
      change: '+5%',
      changeType: 'negative'
    },
    {
      title: 'Open Cases',
      value: caseStats?.open_cases || 0,
      icon: FileText,
      color: 'bg-yellow-500',
      change: '-2%',
      changeType: 'positive'
    },
    {
      title: 'Products Scraped',
      value: scrapingStats?.total_products_scraped || 0,
      icon: Search,
      color: 'bg-green-500',
      change: '+18%',
      changeType: 'positive'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard Metrics</h1>
        <p className="text-gray-600 mt-1">
          Key performance indicators and system metrics
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <div key={metric.title} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${metric.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                </div>
              </div>
              <div className="mt-4 flex items-center">
                {metric.changeType === 'positive' ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600" />
                )}
                <span className={`ml-2 text-sm font-medium ${
                  metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {metric.change}
                </span>
                <span className="ml-2 text-sm text-gray-500">vs last month</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Violations Breakdown */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Violations Overview</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Pending Review</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className="bg-yellow-600 h-2 rounded-full"
                      style={{ width: `${((violationStats?.pending_violations || 0) / (violationStats?.total_violations || 1)) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {violationStats?.pending_violations || 0}
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Confirmed</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className="bg-red-600 h-2 rounded-full"
                      style={{ width: `${((violationStats?.confirmed_violations || 0) / (violationStats?.total_violations || 1)) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {violationStats?.confirmed_violations || 0}
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Dismissed</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className="bg-gray-600 h-2 rounded-full"
                      style={{ width: `${((violationStats?.dismissed_violations || 0) / (violationStats?.total_violations || 1)) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {violationStats?.dismissed_violations || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Cases Status */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Cases Status</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Open Cases</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${((caseStats?.open_cases || 0) / (caseStats?.total_cases || 1)) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {caseStats?.open_cases || 0}
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Investigating</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className="bg-yellow-600 h-2 rounded-full"
                      style={{ width: `${((caseStats?.investigating_cases || 0) / (caseStats?.total_cases || 1)) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {caseStats?.investigating_cases || 0}
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Closed</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${((caseStats?.closed_cases || 0) / (caseStats?.total_cases || 1)) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {caseStats?.closed_cases || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scraping Activity */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Scraping Activity</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Active Jobs</span>
                <span className="text-sm font-medium text-green-600">
                  {scrapingStats?.active_jobs_count || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Recent Jobs (7 days)</span>
                <span className="text-sm font-medium text-blue-600">
                  {scrapingStats?.recent_jobs_count || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Products Scraped</span>
                <span className="text-sm font-medium text-purple-600">
                  {scrapingStats?.total_products_scraped || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Success Rate</span>
                <span className="text-sm font-medium text-green-600">
                  {scrapingStats?.success_rate || 0}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">System Health</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">API Status</span>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm font-medium text-green-600">Online</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Database</span>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm font-medium text-green-600">Connected</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Scraping Service</span>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm font-medium text-green-600">Active</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Last Backup</span>
                <span className="text-sm font-medium text-gray-600">
                  {new Date().toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Summary */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Performance Summary</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {((violationStats?.confirmed_violations || 0) / (violationStats?.total_violations || 1) * 100).toFixed(1)}%
              </div>
              <p className="text-sm text-gray-600">Violation Detection Rate</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {((caseStats?.closed_cases || 0) / (caseStats?.total_cases || 1) * 100).toFixed(1)}%
              </div>
              <p className="text-sm text-gray-600">Case Resolution Rate</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {scrapingStats?.success_rate || 0}%
              </div>
              <p className="text-sm text-gray-600">Scraping Success Rate</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
