'use client'

import { useQuery } from '@tanstack/react-query'
import { violationsApi, casesApi, scrapingApi, productsApi } from '@/lib/api'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { AlertTriangle, FileText, Package, Search } from 'lucide-react'

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

  return (
    <div>
      {/* Page description */}
      <div className="mb-2">
        <p className="text-gray-600">
          Monitor and manage the price regulation system
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatsCard
          title="Total Products"
          value={products?.count || 0}
          icon={Package}
          color="blue"
        />
        <StatsCard
          title="Pending Violations"
          value={violationStats?.pending_violations || 0}
          icon={AlertTriangle}
          color="red"
        />
        <StatsCard
          title="Open Cases"
          value={caseStats?.open_cases || 0}
          icon={FileText}
          color="yellow"
        />
        <StatsCard
          title="Products Scraped"
          value={scrapingStats?.total_products_scraped || 0}
          icon={Search}
          color="green"
        />
      </div>

      {/* Quick actions */}
      <div className="mb-6">
        <QuickActions />
      </div>

      {/* Recent activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity />
        
        {/* System status */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">System Status</h3>
          </div>
          <div className="card-body">
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
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
