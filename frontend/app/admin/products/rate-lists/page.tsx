'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { productsApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Upload, Download, FileText, Calendar, User, Trash2, Eye } from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function RateListsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const { data: rateLists, isLoading, refetch } = useQuery({
    queryKey: ['rate-lists'],
    queryFn: () => productsApi.getRateLists(),
  })

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls') && !file.name.endsWith('.csv')) {
      toast.error('Please upload an Excel or CSV file')
      return
    }

    setSelectedFile(file)
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      
      await productsApi.uploadRateList(formData)
      toast.success('Rate list uploaded successfully')
      setSelectedFile(null)
      refetch()
    } catch (error) {
      toast.error('Failed to upload rate list')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDownload = async (rateListId: string) => {
    try {
      const response = await productsApi.downloadRateList(rateListId)
      const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `rate-list-${rateListId}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      toast.error('Failed to download rate list')
    }
  }

  const handleDelete = async (rateListId: string) => {
    if (!confirm('Are you sure you want to delete this rate list?')) return

    try {
      await productsApi.deleteRateList(rateListId)
      toast.success('Rate list deleted successfully')
      refetch()
    } catch (error) {
      toast.error('Failed to delete rate list')
    }
  }

  // Handle paginated response from API
  const rateListsArray = Array.isArray(rateLists) ? rateLists : rateLists?.results || []
  
  const filteredRateLists = rateListsArray.filter(rateList =>
    rateList.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    rateList.description?.toLowerCase().includes(searchTerm.toLowerCase())
  )

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
          <h1 className="text-2xl font-bold text-gray-900">Rate List Uploads</h1>
          <p className="text-gray-600 mt-1">
            Manage product rate lists and pricing information
          </p>
        </div>
        <div className="flex space-x-3">
          <label className="btn btn-primary cursor-pointer">
            <Upload className="h-4 w-4 mr-2" />
            Upload Rate List
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {/* Upload section */}
      {selectedFile && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <FileText className="h-5 w-5 text-blue-600 mr-3" />
              <div>
                <p className="text-sm font-medium text-blue-900">{selectedFile.name}</p>
                <p className="text-xs text-blue-600">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setSelectedFile(null)}
                className="btn btn-outline btn-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={isUploading}
                className="btn btn-primary btn-sm"
              >
                {isUploading ? (
                  <>
                    <LoadingSpinner size="sm" />
                    Uploading...
                  </>
                ) : (
                  'Upload'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search and filters */}
      <div className="flex justify-between items-center">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search rate lists..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input"
          />
        </div>
        <div className="text-sm text-gray-500">
          {filteredRateLists.length} rate list{filteredRateLists.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Rate lists table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Products Count</th>
                <th>Uploaded By</th>
                <th>Upload Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRateLists.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-500">
                    No rate lists found
                  </td>
                </tr>
              ) : (
                filteredRateLists.map((rateList) => (
                  <tr key={rateList.id}>
                    <td>
                      <div className="flex items-center">
                        <FileText className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="font-medium">{rateList.name}</span>
                      </div>
                    </td>
                    <td>
                      <span className="text-gray-600">
                        {rateList.description || 'No description'}
                      </span>
                    </td>
                    <td>
                      <span className="text-gray-900">{rateList.products_count || 0}</span>
                    </td>
                    <td>
                      <div className="flex items-center">
                        <User className="h-4 w-4 text-gray-400 mr-2" />
                        <span>{rateList.uploaded_by?.name || 'Unknown'}</span>
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                        <span>
                          {new Date(rateList.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${
                        rateList.status === 'active' ? 'badge-success' :
                        rateList.status === 'processing' ? 'badge-warning' :
                        'badge-error'
                      }`}>
                        {rateList.status}
                      </span>
                    </td>
                    <td>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleDownload(rateList.id)}
                          className="btn btn-outline btn-sm"
                          title="Download"
                        >
                          <Download className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {/* View details */}}
                          className="btn btn-outline btn-sm"
                          title="View Details"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(rateList.id)}
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

      {/* Upload instructions */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-3">Upload Instructions</h3>
        <div className="space-y-2 text-sm text-gray-600">
          <p>• Supported formats: Excel (.xlsx, .xls) and CSV files</p>
          <p>• Required columns: Product Name, Category, Regulated Price, Market Price</p>
          <p>• Maximum file size: 10MB</p>
          <p>• The system will automatically process and validate the uploaded data</p>
        </div>
      </div>
    </div>
  )
}
