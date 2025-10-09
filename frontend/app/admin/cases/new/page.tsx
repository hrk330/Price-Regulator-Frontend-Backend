'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { casesApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Save, ArrowLeft, FileText, User, AlertTriangle, Calendar, MapPin } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

interface CaseForm {
  title: string
  description: string
  priority: string
  assigned_to: string
  violation_id?: string
  location: string
  status: string
}

export default function NewCasePage() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<CaseForm>()

  const onSubmit = async (data: CaseForm) => {
    setIsLoading(true)
    try {
      await casesApi.create(data)
      toast.success('Case created successfully')
      router.push('/admin/cases')
    } catch (error) {
      toast.error('Failed to create case')
    } finally {
      setIsLoading(false)
    }
  }

  const priorities = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'urgent', label: 'Urgent' }
  ]

  const statuses = [
    { value: 'open', label: 'Open' },
    { value: 'investigating', label: 'Investigating' },
    { value: 'pending_review', label: 'Pending Review' },
    { value: 'closed', label: 'Closed' }
  ]

  // Mock investigators - in real app, this would come from API
  const investigators = [
    { id: '1', name: 'John Smith' },
    { id: '2', name: 'Sarah Johnson' },
    { id: '3', name: 'Mike Wilson' },
    { id: '4', name: 'Lisa Brown' }
  ]

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Link
            href="/admin/cases"
            className="btn btn-outline btn-sm mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Cases
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Create New Case</h1>
            <p className="text-gray-600 mt-1">
              Start a new investigation case for price violations
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Case Information</h3>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Case Title *
              </label>
              <div className="relative">
                <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('title', { required: 'Case title is required' })}
                  type="text"
                  className="input pl-10"
                  placeholder="Enter case title"
                />
              </div>
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority *
              </label>
              <select
                {...register('priority', { required: 'Priority is required' })}
                className="input"
              >
                <option value="">Select priority</option>
                {priorities.map((priority) => (
                  <option key={priority.value} value={priority.value}>
                    {priority.label}
                  </option>
                ))}
              </select>
              {errors.priority && (
                <p className="mt-1 text-sm text-red-600">{errors.priority.message}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              {...register('description', { required: 'Description is required' })}
              rows={4}
              className="input"
              placeholder="Describe the case details, violations, and investigation requirements"
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          {/* Assignment and Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Assign To
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <select
                  {...register('assigned_to')}
                  className="input pl-10"
                >
                  <option value="">Select investigator</option>
                  {investigators.map((investigator) => (
                    <option key={investigator.id} value={investigator.id}>
                      {investigator.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status *
              </label>
              <select
                {...register('status', { required: 'Status is required' })}
                className="input"
              >
                {statuses.map((status) => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
              {errors.status && (
                <p className="mt-1 text-sm text-red-600">{errors.status.message}</p>
              )}
            </div>
          </div>

          {/* Location and Violation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('location')}
                  type="text"
                  className="input pl-10"
                  placeholder="Enter location (city, state)"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Related Violation ID
              </label>
              <div className="relative">
                <AlertTriangle className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('violation_id')}
                  type="text"
                  className="input pl-10"
                  placeholder="Enter violation ID (optional)"
                />
              </div>
            </div>
          </div>

          {/* Form actions */}
          <div className="border-t pt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => reset()}
              className="btn btn-outline"
            >
              Reset Form
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Creating...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Create Case
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Help section */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">Case Creation Guidelines</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Provide a clear, descriptive title that summarizes the case</p>
          <p>• Include detailed description of violations and investigation requirements</p>
          <p>• Assign appropriate priority level based on severity and urgency</p>
          <p>• Link to related violations when applicable for better tracking</p>
          <p>• Specify location for field investigation cases</p>
        </div>
      </div>
    </div>
  )
}
