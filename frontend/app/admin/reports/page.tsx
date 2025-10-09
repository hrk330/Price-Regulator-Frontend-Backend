'use client'

import { useQuery } from '@tanstack/react-query'
import { reportsApi, violationsApi, casesApi, scrapingApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Download, BarChart3, PieChart, TrendingUp } from 'lucide-react'

export default function ReportsPage() {
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

  const handleExport = async (type: string) => {
    try {
      const data = await reportsApi.export(type)
      const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${type}-report-${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  if (metricsLoading || violationsLoading || casesLoading || scrapingLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div>
      {/* Page header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-gray-600">
            Generate reports and view system analytics
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => handleExport('violations')}
            className="btn btn-primary flex items-center"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Violations
          </button>
          <button
            onClick={() => handleExport('cases')}
            className="btn btn-secondary flex items-center"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Cases
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <BarChart3 className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Violations</p>
                <p className="text-2xl font-bold text-gray-900">
                  {violationStats?.total_violations || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <PieChart className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Open Cases</p>
                <p className="text-2xl font-bold text-gray-900">
                  {caseStats?.open_cases || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
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

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <BarChart3 className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Jobs</p>
                <p className="text-2xl font-bold text-gray-900">
                  {scrapingStats?.active_jobs_count || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Report Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Violations Report */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Violations Summary</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Pending Review</span>
                <span className="text-sm font-medium text-yellow-600">
                  {violationStats?.pending_violations || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Confirmed</span>
                <span className="text-sm font-medium text-red-600">
                  {violationStats?.confirmed_violations || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Dismissed</span>
                <span className="text-sm font-medium text-gray-600">
                  {violationStats?.dismissed_violations || 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Cases Report */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Cases Summary</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Open Cases</span>
                <span className="text-sm font-medium text-blue-600">
                  {caseStats?.open_cases || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Investigating</span>
                <span className="text-sm font-medium text-yellow-600">
                  {caseStats?.investigating_cases || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Closed</span>
                <span className="text-sm font-medium text-green-600">
                  {caseStats?.closed_cases || 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Scraping Report */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Scraping Activity</h3>
          </div>
          <div className="card-body">
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
                <span className="text-sm text-gray-600">Total Products</span>
                <span className="text-sm font-medium text-purple-600">
                  {scrapingStats?.total_products_scraped || 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">System Status</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">API Status</span>
                <span className="text-sm font-medium text-green-600">Online</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Database</span>
                <span className="text-sm font-medium text-green-600">Connected</span>
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
    </div>
  )
}
