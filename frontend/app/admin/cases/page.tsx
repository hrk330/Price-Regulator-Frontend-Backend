'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { casesApi } from '../../lib/api'
import { formatCurrency, formatDate } from '../../lib/utils'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { Plus, Edit, Eye, CheckCircle, XCircle, Search, Filter } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

export default function CasesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('')
  const queryClient = useQueryClient()

  const { data: cases, isLoading } = useQuery({
    queryKey: ['cases', { search: searchTerm, status: selectedStatus }],
    queryFn: () => casesApi.list({ 
      search: searchTerm || undefined,
      status: selectedStatus || undefined,
    }),
  })

  const closeCaseMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => casesApi.close(id, data),
    onSuccess: () => {
      toast.success('Case closed successfully')
      queryClient.invalidateQueries({ queryKey: ['cases'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to close case')
    },
  })

  const handleCloseCase = (caseId: number) => {
    const resolution = window.prompt('Enter case resolution:')
    if (resolution) {
      closeCaseMutation.mutate({
        id: caseId,
        data: { resolution, status: 'closed' }
      })
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'badge-warning'
      case 'closed': return 'badge-success'
      case 'investigating': return 'badge-info'
      default: return 'badge-neutral'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'badge-error'
      case 'medium': return 'badge-warning'
      case 'low': return 'badge-info'
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
          <h1 className="text-2xl font-bold text-gray-900">Cases Management</h1>
          <p className="text-gray-600">
            Manage investigation cases and track their progress
          </p>
        </div>
        <Link
          href="/admin/cases/new"
          className="btn btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Create Case
        </Link>
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
                  placeholder="Search cases..."
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
                <option value="open">Open</option>
                <option value="investigating">Investigating</option>
                <option value="closed">Closed</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Cases table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">
            Cases ({cases?.count || 0})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Title</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Assigned To</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cases?.results?.map((caseItem: any) => (
                <tr key={caseItem.id}>
                  <td>
                    <span className="font-mono text-sm text-gray-600">
                      #{caseItem.id}
                    </span>
                  </td>
                  <td>
                    <div>
                      <p className="font-medium text-gray-900">{caseItem.title}</p>
                      {caseItem.description && (
                        <p className="text-sm text-gray-500 truncate max-w-xs">
                          {caseItem.description}
                        </p>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${getPriorityColor(caseItem.priority)}`}>
                      {caseItem.priority}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${getStatusColor(caseItem.status)}`}>
                      {caseItem.status}
                    </span>
                  </td>
                  <td>
                    <span className="text-gray-600">
                      {caseItem.assigned_to?.name || 'Unassigned'}
                    </span>
                  </td>
                  <td className="text-gray-600">
                    {formatDate(caseItem.created_at)}
                  </td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <Link
                        href={`/admin/cases/${caseItem.id}`}
                        className="p-1 text-gray-400 hover:text-blue-600"
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </Link>
                      <Link
                        href={`/admin/cases/${caseItem.id}/edit`}
                        className="p-1 text-gray-400 hover:text-green-600"
                        title="Edit Case"
                      >
                        <Edit className="h-4 w-4" />
                      </Link>
                      {caseItem.status === 'open' && (
                        <button
                          onClick={() => handleCloseCase(caseItem.id)}
                          className="p-1 text-green-600 hover:text-green-700"
                          disabled={closeCaseMutation.isPending}
                          title="Close Case"
                        >
                          <CheckCircle className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {cases?.results?.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No cases found</p>
            <Link
              href="/admin/cases/new"
              className="btn btn-primary mt-4"
            >
              Create your first case
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
