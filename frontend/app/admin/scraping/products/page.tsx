'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { scrapingApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Package, Search, Filter, Download, Eye, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

export default function ScrapedProductsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [marketplaceFilter, setMarketplaceFilter] = useState('all')

  const { data: scrapedProducts, isLoading } = useQuery({
    queryKey: ['scraped-products'],
    queryFn: () => scrapingApi.getScrapedProducts(),
  })

  // Handle paginated response from API
  const scrapedProductsArray = Array.isArray(scrapedProducts) ? scrapedProducts : scrapedProducts?.results || []
  
  const filteredProducts = scrapedProductsArray.filter((product: any) => {
    const matchesSearch = product.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.marketplace.toLowerCase().includes(searchTerm.toLowerCase())
    // Since there's no status field in the backend, we'll use availability instead
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && product.availability) ||
                         (statusFilter === 'inactive' && !product.availability)
    const matchesMarketplace = marketplaceFilter === 'all' || product.marketplace === marketplaceFilter
    
    return matchesSearch && matchesStatus && matchesMarketplace
  })

  const getStatusIcon = (product: any) => {
    if (product.availability) {
      return <CheckCircle className="h-4 w-4 text-green-600" />
    } else {
      return <XCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusBadge = (product: any) => {
    if (product.availability) {
      return 'badge-success'
    } else {
      return 'badge-neutral'
    }
  }

  const getStatusText = (product: any) => {
    return product.availability ? 'Available' : 'Unavailable'
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Scraped Products</h1>
          <p className="text-gray-600 mt-1">
            View and manage products scraped from various marketplaces
          </p>
        </div>
        <div className="flex space-x-3">
          <button className="btn btn-outline">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Products
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or marketplace..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input"
            >
              <option value="all">All Status</option>
              <option value="active">Available</option>
              <option value="inactive">Unavailable</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Marketplace
            </label>
            <select
              value={marketplaceFilter}
              onChange={(e) => setMarketplaceFilter(e.target.value)}
              className="input"
            >
              <option value="all">All Marketplaces</option>
              <option value="amazon">Amazon</option>
              <option value="flipkart">Flipkart</option>
              <option value="myntra">Myntra</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('')
                setStatusFilter('all')
                setMarketplaceFilter('all')
              }}
              className="btn btn-outline w-full"
            >
              <Filter className="h-4 w-4 mr-2" />
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Package className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Products</p>
              <p className="text-2xl font-bold text-gray-900">
                {scrapedProductsArray.length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-bold text-gray-900">
                {scrapedProductsArray.filter((p: any) => p.availability).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Violations</p>
              <p className="text-2xl font-bold text-gray-900">
                {scrapedProductsArray.filter((p: any) => !p.availability).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-gray-100 rounded-lg">
              <XCircle className="h-6 w-6 text-gray-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Inactive</p>
              <p className="text-2xl font-bold text-gray-900">
                {scrapedProductsArray.filter((p: any) => !p.availability).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Products table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Marketplace</th>
                <th>Current Price</th>
                <th>Regulated Price</th>
                <th>Difference</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-gray-500">
                    No scraped products found
                  </td>
                </tr>
              ) : (
                filteredProducts.map((product: any) => (
                  <tr key={product.id}>
                    <td>
                      <div className="flex items-center">
                        <Package className="h-4 w-4 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium text-gray-900">{product.product_name}</p>
                          <p className="text-sm text-gray-500">{product.marketplace}</p>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="text-gray-900 capitalize">{product.marketplace}</span>
                    </td>
                    <td>
                      <span className="font-medium text-gray-900">
                        ₹{product.current_price?.toFixed(2) || 'N/A'}
                      </span>
                    </td>
                    <td>
                      <span className="text-gray-600">
                        ₹{product.regulated_price?.toFixed(2) || 'N/A'}
                      </span>
                    </td>
                    <td>
                      <span className={`font-medium ${
                        (product.current_price || 0) > (product.regulated_price || 0) 
                          ? 'text-red-600' 
                          : 'text-green-600'
                      }`}>
                        {product.regulated_price && product.current_price 
                          ? `₹${(product.current_price - product.regulated_price).toFixed(2)}`
                          : 'N/A'
                        }
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center">
                        {getStatusIcon(product)}
                        <span className={`ml-2 badge ${getStatusBadge(product)}`}>
                          {getStatusText(product)}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="text-gray-600">
                        {new Date(product.last_updated).toLocaleDateString()}
                      </span>
                    </td>
                    <td>
                      <div className="flex space-x-2">
                        <button
                          className="btn btn-outline btn-sm"
                          title="View Details"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {filteredProducts.length > 0 && (
        <div className="flex justify-between items-center">
          <p className="text-sm text-gray-700">
            Showing {filteredProducts.length} of {scrapedProductsArray.length} products
          </p>
          <div className="flex space-x-2">
            <button className="btn btn-outline btn-sm">Previous</button>
            <button className="btn btn-outline btn-sm">Next</button>
          </div>
        </div>
      )}
    </div>
  )
}
