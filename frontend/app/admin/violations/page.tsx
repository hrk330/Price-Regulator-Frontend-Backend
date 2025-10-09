'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { violationsApi } from '@/lib/api'
import { formatCurrency, formatDate } from '@/lib/utils'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Check, X, AlertTriangle, Search, Filter } from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function ViolationsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('')
  const [selectedSeverity, setSelectedSeverity] = useState('')
  const queryClient = useQueryClient()

  const { data: violations, isLoading } = useQuery({
    queryKey: ['violations', { search: searchTerm, status: selectedStatus, severity: selectedSeverity }],
    queryFn: () => violationsApi.list({ 
      search: searchTerm || undefined,
      status: selectedStatus || undefined,
      severity: selectedSeverity || undefined,
    }),
  })

  const confirmViolationMutation = useMutation({
    mutationFn: (id: number) => violationsApi.confirm(id),
    onSuccess: () => {
      toast.success('Violation confirmed successfully')
      queryClient.invalidateQueries({ queryKey: ['violations'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to confirm violation')
    },
  })

  const dismissViolationMutation = useMutation({
    mutationFn: (id: number) => violationsApi.dismiss(id),
    onSuccess: () => {
      toast.success('Violation dismissed successfully')
      queryClient.invalidateQueries({ queryKey: ['violations'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to dismiss violation')
    },
  })

  const handleConfirm = (id: number) => {
    if (window.confirm('Are you sure you want to confirm this violation?')) {
      confirmViolationMutation.mutate(id)
    }
  }

  const handleDismiss = (id: number) => {
    if (window.confirm('Are you sure you want to dismiss this violation?')) {
      dismissViolationMutation.mutate(id)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'badge-error'
      case 'medium': return 'badge-warning'
      case 'low': return 'badge-info'
      default: return 'badge-neutral'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'badge-success'
      case 'dismissed': return 'badge-neutral'
      case 'pending': return 'badge-warning'
      default: return 'badge-neutral'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div>
      {/* Page header */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Violations Management</h1>
          <p className="text-gray-600">
            Review and manage price violations detected by the system
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="card-body">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search violations..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="input"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="dismissed">Dismissed</option>
              </select>
            </div>
            <div className="sm:w-48">
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="input"
              >
                <option value="">All Severities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Violations table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">
            Violations ({violations?.count || 0})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Violation Type</th>
                <th>Severity</th>
                <th>Price Difference</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {violations?.results?.map((violation: any) => (
                <tr key={violation.id}>
                  <td>
                    <div>
                      <p className="font-medium text-gray-900">
                        {violation.regulated_product?.name || 'Unknown Product'}
                      </p>
                      <p className="text-sm text-gray-500">
                        Found: {violation.scraped_product_name}
                      </p>
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-warning">
                      {violation.violation_type}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${getSeverityColor(violation.severity)}`}>
                      {violation.severity}
                    </span>
                  </td>
                  <td>
                    <div>
                      <p className="font-medium text-red-600">
                        {formatCurrency(violation.price_difference)}
                      </p>
                      <p className="text-sm text-gray-500">
                        {violation.percentage_over}% over
                      </p>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${getStatusColor(violation.status)}`}>
                      {violation.status}
                    </span>
                  </td>
                  <td className="text-gray-600">
                    {formatDate(violation.created_at)}
                  </td>
                  <td>
                    <div className="flex items-center space-x-2">
                      {violation.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleConfirm(violation.id)}
                            className="p-1 text-green-600 hover:text-green-700"
                            disabled={confirmViolationMutation.isPending}
                            title="Confirm Violation"
                          >
                            <Check className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDismiss(violation.id)}
                            className="p-1 text-red-600 hover:text-red-700"
                            disabled={dismissViolationMutation.isPending}
                            title="Dismiss Violation"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => violationsApi.get(violation.id)}
                        className="p-1 text-gray-400 hover:text-blue-600"
                        title="View Details"
                      >
                        <AlertTriangle className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {violations?.results?.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No violations found</p>
          </div>
        )}
      </div>
    </div>
  )
}
