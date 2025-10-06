'use client'

import { useQuery } from '@tanstack/react-query'
import { reportsApi } from '@/lib/api'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { ViolationsChart } from '@/components/regulator/ViolationsChart'
import { TopViolatingProducts } from '@/components/regulator/TopViolatingProducts'
import { MarketplaceBreakdown } from '@/components/regulator/MarketplaceBreakdown'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { AlertTriangle, FileText, DollarSign, TrendingUp } from 'lucide-react'

export default function RegulatorDashboard() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['report-summary'],
    queryFn: reportsApi.summary,
  })

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: reportsApi.dashboardMetrics,
  })

  if (summaryLoading || metricsLoading) {
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
          Monitor price regulation compliance and enforcement metrics
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatsCard
          title="Total Violations"
          value={summary?.total_violations || 0}
          icon={AlertTriangle}
          color="red"
        />
        <StatsCard
          title="Total Cases"
          value={summary?.total_cases || 0}
          icon={FileText}
          color="blue"
        />
        <StatsCard
          title="Total Penalties"
          value={`$${summary?.total_penalties?.toLocaleString() || 0}`}
          icon={DollarSign}
          color="green"
        />
        <StatsCard
          title="Active Products"
          value={summary?.total_products || 0}
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Charts and analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ViolationsChart data={metrics?.violations_timeline} />
        <MarketplaceBreakdown data={metrics?.violations_by_marketplace} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopViolatingProducts data={metrics?.top_violating_products} />
        
        {/* Violation severity breakdown */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Violation Severity</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {Object.entries(summary?.violations_by_severity || {}).map(([severity, count]) => (
                <div key={severity} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      severity === 'low' ? 'bg-green-500' :
                      severity === 'medium' ? 'bg-yellow-500' :
                      severity === 'high' ? 'bg-red-500' :
                      'bg-purple-500'
                    }`} />
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {severity}
                    </span>
                  </div>
                  <span className="text-sm text-gray-600">{count as number}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Case status breakdown */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Case Status Overview</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Object.entries(summary?.cases_by_status || {}).map(([status, count]) => (
              <div key={status} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{count as number}</div>
                <div className="text-sm text-gray-600 capitalize">
                  {status.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
