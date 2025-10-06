'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { scrapingApi } from '@/lib/api'
import { Plus, Play, Package, AlertTriangle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

export function QuickActions() {
  const [selectedMarketplace, setSelectedMarketplace] = useState('amazon')
  const queryClient = useQueryClient()

  const triggerScrapingMutation = useMutation({
    mutationFn: (marketplace: string) => scrapingApi.trigger(marketplace),
    onSuccess: () => {
      toast.success('Scraping job started successfully')
      queryClient.invalidateQueries({ queryKey: ['scraping-stats'] })
      queryClient.invalidateQueries({ queryKey: ['scraping-jobs'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to start scraping job')
    },
  })

  const handleTriggerScraping = () => {
    triggerScrapingMutation.mutate(selectedMarketplace)
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
      </div>
      <div className="card-body">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Add Product */}
          <Link
            href="/dashboard/admin/products/new"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="p-2 bg-blue-50 rounded-lg">
              <Plus className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Add Product</p>
              <p className="text-xs text-gray-500">Register new regulated product</p>
            </div>
          </Link>

          {/* Trigger Scraping */}
          <div className="flex items-center p-4 border border-gray-200 rounded-lg">
            <div className="p-2 bg-green-50 rounded-lg">
              <Play className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-900">Start Scraping</p>
              <div className="flex items-center space-x-2 mt-1">
                <select
                  value={selectedMarketplace}
                  onChange={(e) => setSelectedMarketplace(e.target.value)}
                  className="text-xs border border-gray-300 rounded px-2 py-1"
                >
                  <option value="amazon">Amazon</option>
                  <option value="ebay">eBay</option>
                  <option value="walmart">Walmart</option>
                  <option value="target">Target</option>
                </select>
                <button
                  onClick={handleTriggerScraping}
                  disabled={triggerScrapingMutation.isPending}
                  className="btn btn-success text-xs px-2 py-1"
                >
                  {triggerScrapingMutation.isPending ? 'Starting...' : 'Start'}
                </button>
              </div>
            </div>
          </div>

          {/* View Products */}
          <Link
            href="/dashboard/admin/products"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="p-2 bg-purple-50 rounded-lg">
              <Package className="h-5 w-5 text-purple-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Manage Products</p>
              <p className="text-xs text-gray-500">View and edit products</p>
            </div>
          </Link>

          {/* View Violations */}
          <Link
            href="/dashboard/admin/violations"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="p-2 bg-red-50 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">View Violations</p>
              <p className="text-xs text-gray-500">Review pending violations</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
