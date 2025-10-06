'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { productsApi } from '@/lib/api'
import { formatCurrency, formatDate } from '@/lib/utils'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Plus, Edit, Trash2, Search } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

export default function ProductsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const queryClient = useQueryClient()

  const { data: products, isLoading } = useQuery({
    queryKey: ['products', { search: searchTerm, category: selectedCategory }],
    queryFn: () => productsApi.list({ 
      search: searchTerm || undefined,
      category: selectedCategory || undefined,
    }),
  })

  const { data: categories } = useQuery({
    queryKey: ['product-categories'],
    queryFn: productsApi.categories,
  })

  const deleteProductMutation = useMutation({
    mutationFn: (id: number) => productsApi.delete(id),
    onSuccess: () => {
      toast.success('Product deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to delete product')
    },
  })

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
      deleteProductMutation.mutate(id)
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
          <p className="text-gray-600">
            Manage regulated products and their government prices
          </p>
        </div>
        <Link
          href="/dashboard/admin/products/new"
          className="btn btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Product
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
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="input"
              >
                <option value="">All Categories</option>
                {categories?.categories?.map((category: string) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Products table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">
            Products ({products?.count || 0})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Government Price</th>
                <th>Unit</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products?.results?.map((product: any) => (
                <tr key={product.id}>
                  <td>
                    <div>
                      <p className="font-medium text-gray-900">{product.name}</p>
                      {product.description && (
                        <p className="text-sm text-gray-500 truncate max-w-xs">
                          {product.description}
                        </p>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-info">{product.category}</span>
                  </td>
                  <td className="font-medium">
                    {formatCurrency(product.gov_price)}
                  </td>
                  <td className="text-gray-600">{product.unit}</td>
                  <td>
                    <span className={`badge ${product.is_active ? 'badge-success' : 'badge-warning'}`}>
                      {product.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="text-gray-600">
                    {formatDate(product.created_at)}
                  </td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <Link
                        href={`/dashboard/admin/products/${product.id}/edit`}
                        className="p-1 text-gray-400 hover:text-blue-600"
                      >
                        <Edit className="h-4 w-4" />
                      </Link>
                      <button
                        onClick={() => handleDelete(product.id, product.name)}
                        className="p-1 text-gray-400 hover:text-red-600"
                        disabled={deleteProductMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {products?.results?.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No products found</p>
            <Link
              href="/dashboard/admin/products/new"
              className="btn btn-primary mt-4"
            >
              Add your first product
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
