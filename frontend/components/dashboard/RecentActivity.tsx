'use client'

import { useQuery } from '@tanstack/react-query'
import { violationsApi } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

export function RecentActivity() {
  const { data: violations, isLoading } = useQuery({
    queryKey: ['recent-violations'],
    queryFn: () => violationsApi.list({ page_size: 5 }),
  })

  if (isLoading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
        </div>
        <div className="card-body">
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        </div>
      </div>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'dismissed':
        return <XCircle className="h-4 w-4 text-gray-500" />
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'text-green-600'
      case 'dismissed':
        return 'text-gray-600'
      default:
        return 'text-yellow-600'
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Recent Violations</h3>
      </div>
      <div className="card-body">
        {violations?.results?.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No recent violations</p>
        ) : (
          <div className="space-y-4">
            {violations?.results?.map((violation: any) => (
              <div key={violation.id} className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  {getStatusIcon(violation.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {violation.regulated_product.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {violation.scraped_product.marketplace} - ${violation.scraped_product.listed_price}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`text-xs font-medium ${getStatusColor(violation.status)}`}>
                      {violation.status}
                    </span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-400">
                      {formatDate(violation.created_at)}
                    </span>
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    {violation.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
