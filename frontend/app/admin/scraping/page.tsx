'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { scrapingApi } from '@/lib/api'
import { formatCurrency, formatDate } from '@/lib/utils'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Plus, Play, Pause, Trash2, Search, Filter } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

export default function ScrapingPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedMarketplace, setSelectedMarketplace] = useState('')
  const queryClient = useQueryClient()

  const { data: scrapingJobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['scraping-jobs'],
    queryFn: scrapingApi.jobs,
  })

  const { data: scrapedProducts, isLoading: productsLoading } = useQuery({
    queryKey: ['scraped-products', { search: searchTerm, marketplace: selectedMarketplace }],
    queryFn: () => scrapingApi.results({ 
      search: searchTerm || undefined,
      marketplace: selectedMarketplace || undefined,
    }),
  })

  const triggerScrapingMutation = useMutation({
    mutationFn: (marketplace: string) => scrapingApi.trigger(marketplace),
    onSuccess: () => {
      toast.success('Scraping job triggered successfully')
      queryClient.invalidateQueries({ queryKey: ['scraping-jobs'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to trigger scraping')
    },
  })

  const handleTriggerScraping = (marketplace: string) => {
    if (window.confirm(`Start scraping for ${marketplace}?`)) {
      triggerScrapingMutation.mutate(marketplace)
    }
  }

  if (jobsLoading || productsLoading) {
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
          <h1 className="text-2xl font-bold text-gray-900">Scraping Management</h1>
          <p className="text-gray-600">
            Manage scraping jobs and view scraped product data
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => handleTriggerScraping('kissan')}
            className="btn btn-primary flex items-center"
            disabled={triggerScrapingMutation.isPending}
          >
            <Play className="h-4 w-4 mr-2" />
            Start Kissan Scraping
          </button>
          <button
            onClick={() => handleTriggerScraping('daraz')}
            className="btn btn-secondary flex items-center"
            disabled={triggerScrapingMutation.isPending}
          >
            <Play className="h-4 w-4 mr-2" />
            Start Daraz Scraping
          </button>
        </div>
      </div>

      {/* Active Jobs */}
      <div className="card mb-6">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Active Scraping Jobs</h3>
        </div>
        <div className="card-body">
          {scrapingJobs?.length === 0 ? (
            <p className="text-gray-500">No active scraping jobs</p>
          ) : (
            <div className="space-y-4">
              {scrapingJobs?.map((job: any) => (
                <div key={job.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">{job.marketplace}</h4>
                    <p className="text-sm text-gray-600">
                      Status: <span className="font-medium">{job.status}</span>
                    </p>
                    <p className="text-sm text-gray-600">
                      Started: {formatDate(job.started_at)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`badge ${job.status === 'running' ? 'badge-success' : 'badge-warning'}`}>
                      {job.status}
                    </span>
                    {job.status === 'running' && (
                      <button className="btn btn-sm btn-outline">
                        <Pause className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
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
                  placeholder="Search scraped products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={selectedMarketplace}
                onChange={(e) => setSelectedMarketplace(e.target.value)}
                className="input"
              >
                <option value="">All Marketplaces</option>
                <option value="kissan">Kissan</option>
                <option value="daraz">Daraz</option>
                <option value="olx">OLX</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Scraped Products */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">
            Scraped Products ({scrapedProducts?.count || 0})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Marketplace</th>
                <th>Price</th>
                <th>Availability</th>
                <th>Scraped At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {scrapedProducts?.results?.map((product: any) => (
                <tr key={product.id}>
                  <td>
                    <div>
                      <p className="font-medium text-gray-900">{product.product_name}</p>
                      {product.description && (
                        <p className="text-sm text-gray-500 truncate max-w-xs">
                          {product.description}
                        </p>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-info">{product.marketplace}</span>
                  </td>
                  <td className="font-medium">
                    {formatCurrency(product.listed_price)}
                  </td>
                  <td>
                    <span className={`badge ${product.availability ? 'badge-success' : 'badge-warning'}`}>
                      {product.availability ? 'Available' : 'Out of Stock'}
                    </span>
                  </td>
                  <td className="text-gray-600">
                    {formatDate(product.scraped_at)}
                  </td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 text-gray-400 hover:text-blue-600"
                      >
                        <Search className="h-4 w-4" />
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {scrapedProducts?.results?.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No scraped products found</p>
            <button
              onClick={() => handleTriggerScraping('kissan')}
              className="btn btn-primary mt-4"
            >
              Start Scraping
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
