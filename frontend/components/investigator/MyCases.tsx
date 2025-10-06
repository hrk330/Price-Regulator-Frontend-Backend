'use client'

import { useQuery } from '@tanstack/react-query'
import { casesApi } from '@/lib/api'
import { formatDate, getStatusColor } from '@/lib/utils'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { FileText, Clock, CheckCircle } from 'lucide-react'
import Link from 'next/link'

export function MyCases() {
  const { data: cases, isLoading } = useQuery({
    queryKey: ['my-cases'],
    queryFn: () => casesApi.list({ page_size: 5 }),
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'in_progress':
        return <FileText className="h-4 w-4 text-blue-500" />
      case 'closed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      default:
        return <FileText className="h-4 w-4 text-gray-500" />
    }
  }

  if (isLoading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">My Cases</h3>
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
          <h3 className="text-lg font-medium text-gray-900">My Cases</h3>
          <Link
            href="/dashboard/investigator/cases"
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            View all
          </Link>
        </div>
      </div>
      <div className="card-body">
        {cases?.results?.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No cases assigned</p>
        ) : (
          <div className="space-y-4">
            {cases?.results?.map((caseItem: any) => (
              <div key={caseItem.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(caseItem.status)}
                      <h4 className="font-medium text-gray-900">
                        Case #{caseItem.id}
                      </h4>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {caseItem.violation.regulated_product.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {caseItem.violation.scraped_product.marketplace} - 
                      ${caseItem.violation.scraped_product.listed_price}
                    </p>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className={`badge ${getStatusColor(caseItem.status)}`}>
                        {caseItem.status.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDate(caseItem.created_at)}
                      </span>
                    </div>
                    {caseItem.notes && (
                      <p className="text-sm text-gray-600 mt-2 truncate">
                        {caseItem.notes}
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="mt-4">
                  <Link
                    href={`/dashboard/investigator/cases/${caseItem.id}`}
                    className="btn btn-primary text-sm"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
