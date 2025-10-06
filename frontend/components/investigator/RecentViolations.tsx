'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { violationsApi } from '@/lib/api'
import { formatDate, formatCurrency } from '@/lib/utils'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

export function RecentViolations() {
  const queryClient = useQueryClient()

  const { data: violations, isLoading } = useQuery({
    queryKey: ['recent-violations'],
    queryFn: () => violationsApi.list({ page_size: 5, status: 'pending' }),
  })

  const confirmMutation = useMutation({
    mutationFn: (id: number) => violationsApi.confirm(id),
    onSuccess: () => {
      toast.success('Violation confirmed and case created')
      queryClient.invalidateQueries({ queryKey: ['recent-violations'] })
      queryClient.invalidateQueries({ queryKey: ['case-stats'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to confirm violation')
    },
  })

  const dismissMutation = useMutation({
    mutationFn: (id: number) => violationsApi.dismiss(id),
    onSuccess: () => {
      toast.success('Violation dismissed')
      queryClient.invalidateQueries({ queryKey: ['recent-violations'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to dismiss violation')
    },
  })

  const handleConfirm = (id: number) => {
    if (window.confirm('Are you sure you want to confirm this violation? A case will be created.')) {
      confirmMutation.mutate(id)
    }
  }

  const handleDismiss = (id: number) => {
    if (window.confirm('Are you sure you want to dismiss this violation?')) {
      dismissMutation.mutate(id)
    }
  }

  if (isLoading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Recent Violations</h3>
        </div>
        <div className="card-body">
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Pending Violations</h3>
          <Link
            href="/dashboard/investigator/violations"
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            View all
          </Link>
        </div>
      </div>
      <div className="card-body">
        {violations?.results?.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No pending violations</p>
        ) : (
          <div className="space-y-4">
            {violations?.results?.map((violation: any) => (
              <div key={violation.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">
                      {violation.regulated_product.name}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {violation.scraped_product.marketplace} - {violation.scraped_product.product_name}
                    </p>
                    <div className="flex items-center space-x-4 mt-2 text-sm">
                      <span className="text-gray-500">
                        Listed: {formatCurrency(violation.scraped_product.listed_price)}
                      </span>
                      <span className="text-gray-500">
                        Gov: {formatCurrency(violation.regulated_product.gov_price)}
                      </span>
                      <span className="text-red-600 font-medium">
                        +{violation.percentage_over.toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className={`badge ${
                        violation.severity === 'low' ? 'badge-success' :
                        violation.severity === 'medium' ? 'badge-warning' :
                        'badge-danger'
                      }`}>
                        {violation.severity}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDate(violation.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 mt-4">
                  <button
                    onClick={() => handleConfirm(violation.id)}
                    disabled={confirmMutation.isPending}
                    className="btn btn-success text-sm flex items-center"
                  >
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Confirm
                  </button>
                  <button
                    onClick={() => handleDismiss(violation.id)}
                    disabled={dismissMutation.isPending}
                    className="btn btn-secondary text-sm flex items-center"
                  >
                    <XCircle className="h-4 w-4 mr-1" />
                    Dismiss
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
