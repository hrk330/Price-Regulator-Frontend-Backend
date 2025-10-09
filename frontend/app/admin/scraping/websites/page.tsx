'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { scrapingApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Globe, Plus, Edit, Trash2, Play, Pause, Eye, Settings, CheckCircle, XCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function ScrapingWebsitesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  const { data: websites, isLoading, refetch } = useQuery({
    queryKey: ['scraping-websites'],
    queryFn: () => scrapingApi.getScrapingWebsites(),
  })

  // Handle paginated response from API
  const websitesArray = Array.isArray(websites) ? websites : websites?.results || []
  
  const filteredWebsites = websitesArray.filter((website: any) =>
    website.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    website.url.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCreateWebsite = async () => {
    setIsCreating(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Scraping website added successfully')
      refetch()
    } catch (error) {
      toast.error('Failed to add scraping website')
    } finally {
      setIsCreating(false)
    }
  }

  const handleToggleStatus = async (websiteId: string, currentStatus: boolean) => {
    try {
      const newStatus = !currentStatus
      await scrapingApi.updateWebsiteStatus(websiteId, newStatus ? 'active' : 'inactive')
      toast.success(`Website ${newStatus ? 'activated' : 'deactivated'}`)
      refetch()
    } catch (error) {
      toast.error('Failed to update website status')
    }
  }

  const handleDelete = async (websiteId: string) => {
    if (!confirm('Are you sure you want to delete this website?')) return

    try {
      await scrapingApi.deleteWebsite(websiteId)
      toast.success('Website deleted successfully')
      refetch()
    } catch (error) {
      toast.error('Failed to delete website')
    }
  }

  const getStatusIcon = (isActive: boolean) => {
    if (isActive) {
      return <CheckCircle className="h-4 w-4 text-green-600" />
    } else {
      return <XCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusBadge = (isActive: boolean) => {
    if (isActive) {
      return 'badge-success'
    } else {
      return 'badge-neutral'
    }
  }

  const getStatusText = (isActive: boolean) => {
    return isActive ? 'Active' : 'Inactive'
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
          <h1 className="text-2xl font-bold text-gray-900">Scraping Websites</h1>
          <p className="text-gray-600 mt-1">
            Manage websites and marketplaces for product scraping
          </p>
        </div>
        <button
          onClick={handleCreateWebsite}
          disabled={isCreating}
          className="btn btn-primary"
        >
          {isCreating ? (
            <>
              <LoadingSpinner size="sm" />
              Adding...
            </>
          ) : (
            <>
              <Plus className="h-4 w-4 mr-2" />
              Add Website
            </>
          )}
        </button>
      </div>

      {/* Search */}
      <div className="flex justify-between items-center">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search websites..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input"
          />
        </div>
        <div className="text-sm text-gray-500">
          {filteredWebsites.length} website{filteredWebsites.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Globe className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Websites</p>
              <p className="text-2xl font-bold text-gray-900">
                {websitesArray.length}
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
                {websitesArray.filter((w: any) => w.is_active).length}
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
                {websitesArray.filter((w: any) => !w.is_active).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <XCircle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Errors</p>
              <p className="text-2xl font-bold text-gray-900">
                {websitesArray.filter((w: any) => !w.is_active).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Websites table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Website</th>
                <th>URL</th>
                <th>Type</th>
                <th>Status</th>
                <th>Last Scraped</th>
                <th>Products Found</th>
                <th>Success Rate</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredWebsites.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-gray-500">
                    No websites found
                  </td>
                </tr>
              ) : (
                filteredWebsites.map((website: any) => (
                  <tr key={website.id}>
                    <td>
                      <div className="flex items-center">
                        <Globe className="h-4 w-4 text-gray-400 mr-3" />
                        <span className="font-medium">{website.name}</span>
                      </div>
                    </td>
                    <td>
                      <a
                        href={website.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        {website.url}
                      </a>
                    </td>
                    <td>
                      <span className="badge badge-info capitalize">
                        {website.type || 'marketplace'}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center">
                        {getStatusIcon(website.is_active)}
                        <span className={`ml-2 badge ${getStatusBadge(website.is_active)}`}>
                          {getStatusText(website.is_active)}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="text-gray-600">
                        {website.last_scraped ? new Date(website.last_scraped).toLocaleDateString() : 'Never'}
                      </span>
                    </td>
                    <td>
                      <span className="text-gray-900">{website.products_found || 0}</span>
                    </td>
                    <td>
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: `${website.success_rate || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">
                          {website.success_rate || 0}%
                        </span>
                      </div>
                    </td>
                    <td>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleToggleStatus(website.id, website.is_active)}
                          className={`btn btn-sm ${
                            website.is_active ? 'btn-outline' : 'btn-primary'
                          }`}
                          title={website.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {website.is_active ? (
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
                          title="Configure"
                        >
                          <Settings className="h-4 w-4" />
                        </button>
                        <button
                          className="btn btn-outline btn-sm"
                          title="Edit"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(website.id)}
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
        <h3 className="text-lg font-medium text-blue-900 mb-3">About Scraping Websites</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Add websites and marketplaces where products should be scraped from</p>
          <p>• Configure scraping settings for each website (selectors, delays, etc.)</p>
          <p>• Monitor success rates and scraping performance</p>
          <p>• Only active websites will be used during scraping jobs</p>
        </div>
      </div>
    </div>
  )
}
