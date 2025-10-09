'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { scrapingApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Search, Plus, Edit, Trash2, Play, Pause, Eye, FileText } from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function SearchListsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  const { data: searchLists, isLoading, refetch } = useQuery({
    queryKey: ['search-lists'],
    queryFn: () => scrapingApi.getSearchLists(),
  })

  // Handle paginated response from API
  const searchListsArray = Array.isArray(searchLists) ? searchLists : searchLists?.results || []
  
  const filteredLists = searchListsArray.filter(list =>
    list.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    list.description?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCreateList = async () => {
    setIsCreating(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Search list created successfully')
      refetch()
    } catch (error) {
      toast.error('Failed to create search list')
    } finally {
      setIsCreating(false)
    }
  }

  const handleToggleStatus = async (listId: string, currentStatus: boolean) => {
    try {
      const newStatus = !currentStatus
      await scrapingApi.updateSearchListStatus(listId, newStatus ? 'active' : 'inactive')
      toast.success(`Search list ${newStatus ? 'activated' : 'deactivated'}`)
      refetch()
    } catch (error) {
      toast.error('Failed to update search list status')
    }
  }

  const handleDelete = async (listId: string) => {
    if (!confirm('Are you sure you want to delete this search list?')) return

    try {
      await scrapingApi.deleteSearchList(listId)
      toast.success('Search list deleted successfully')
      refetch()
    } catch (error) {
      toast.error('Failed to delete search list')
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
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Product Search Lists</h1>
          <p className="text-gray-600 mt-1">
            Manage search terms and keywords for product scraping
          </p>
        </div>
        <button
          onClick={handleCreateList}
          disabled={isCreating}
          className="btn btn-primary"
        >
          {isCreating ? (
            <>
              <LoadingSpinner size="sm" />
              Creating...
            </>
          ) : (
            <>
              <Plus className="h-4 w-4 mr-2" />
              Create Search List
            </>
          )}
        </button>
      </div>

      {/* Search */}
      <div className="flex justify-between items-center">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search lists..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <div className="text-sm text-gray-500">
          {filteredLists.length} search list{filteredLists.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Lists</p>
              <p className="text-2xl font-bold text-gray-900">
                {searchLists?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Play className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-bold text-gray-900">
                {searchListsArray.filter(l => l.is_active).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Pause className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Inactive</p>
              <p className="text-2xl font-bold text-gray-900">
                {searchListsArray.filter(l => !l.is_active).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Search className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Keywords</p>
              <p className="text-2xl font-bold text-gray-900">
                {searchLists?.reduce((total, list) => total + (list.keywords?.length || 0), 0) || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Search lists table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Keywords</th>
                <th>Status</th>
                <th>Last Used</th>
                <th>Products Found</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredLists.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-500">
                    No search lists found
                  </td>
                </tr>
              ) : (
                filteredLists.map((list) => (
                  <tr key={list.id}>
                    <td>
                      <div className="flex items-center">
                        <FileText className="h-4 w-4 text-gray-400 mr-3" />
                        <span className="font-medium">{list.name}</span>
                      </div>
                    </td>
                    <td>
                      <span className="text-gray-600">
                        {list.description || 'No description'}
                      </span>
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {list.keywords?.slice(0, 3).map((keyword, index) => (
                          <span
                            key={index}
                            className="badge badge-info text-xs"
                          >
                            {keyword}
                          </span>
                        ))}
                        {list.keywords && list.keywords.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{list.keywords.length - 3} more
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${
                        list.is_active ? 'badge-success' : 'badge-neutral'
                      }`}>
                        {list.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <span className="text-gray-600">
                        {list.last_used ? new Date(list.last_used).toLocaleDateString() : 'Never'}
                      </span>
                    </td>
                    <td>
                      <span className="text-gray-900">{list.products_found || 0}</span>
                    </td>
                    <td>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleToggleStatus(list.id, list.is_active)}
                          className={`btn btn-sm ${
                            list.is_active ? 'btn-outline' : 'btn-primary'
                          }`}
                          title={list.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {list.is_active ? (
                            <Pause className="h-4 w-4" />
                          ) : (
                            <Play className="h-4 w-4" />
                          )}
                        </button>
                        <button
                          className="btn btn-outline btn-sm"
                          title="View Details"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          className="btn btn-outline btn-sm"
                          title="Edit"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(list.id)}
                          className="btn btn-outline btn-sm text-red-600 hover:bg-red-50"
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
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

      {/* Help section */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">About Search Lists</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Search lists contain keywords and terms used to find products on marketplaces</p>
          <p>• Active lists are automatically used during scraping jobs</p>
          <p>• You can create multiple lists for different product categories</p>
          <p>• Keywords should be relevant and specific to the products you want to monitor</p>
        </div>
      </div>
    </div>
  )
}
