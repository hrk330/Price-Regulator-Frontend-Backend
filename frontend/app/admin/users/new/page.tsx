'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { usersApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Save, ArrowLeft, User, Mail, Lock, Shield, Phone, MapPin } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

interface UserForm {
  name: string
  email: string
  password: string
  confirmPassword: string
  role: string
  phone?: string
  department?: string
  location?: string
  is_active: boolean
}

export default function NewUserPage() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch
  } = useForm<UserForm>()

  const password = watch('password')

  const onSubmit = async (data: UserForm) => {
    if (data.password !== data.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    setIsLoading(true)
    try {
      const { confirmPassword, ...userData } = data
      await usersApi.create(userData)
      toast.success('User created successfully')
      router.push('/admin/users')
    } catch (error) {
      toast.error('Failed to create user')
    } finally {
      setIsLoading(false)
    }
  }

  const roles = [
    { value: 'admin', label: 'Administrator', description: 'Full system access' },
    { value: 'investigator', label: 'Investigator', description: 'Case management and investigation' },
    { value: 'regulator', label: 'Regulator', description: 'Reports and analytics access' }
  ]

  const departments = [
    'Price Monitoring',
    'Investigation',
    'Compliance',
    'Legal',
    'IT Support',
    'Management'
  ]

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Link
            href="/admin/users"
            className="btn btn-outline btn-sm mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Users
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Add New User</h1>
            <p className="text-gray-600 mt-1">
              Create a new user account for the system
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">User Information</h3>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('name', { required: 'Full name is required' })}
                  type="text"
                  className="input pl-10"
                  placeholder="Enter full name"
                />
              </div>
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('email', { 
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address'
                    }
                  })}
                  type="email"
                  className="input pl-10"
                  placeholder="Enter email address"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>
          </div>

          {/* Contact Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('phone')}
                  type="tel"
                  className="input pl-10"
                  placeholder="Enter phone number"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Department
              </label>
              <select
                {...register('department')}
                className="input"
              >
                <option value="">Select department</option>
                {departments.map((dept) => (
                  <option key={dept} value={dept}>
                    {dept}
                  </option>
                ))}
              </select>
            </div>
          </div>

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

          {/* Role and Access */}
          <div className="border-t pt-6">
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Role and Access
            </h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User Role *
                </label>
                <select
                  {...register('role', { required: 'Role is required' })}
                  className="input"
                >
                  <option value="">Select role</option>
                  {roles.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label} - {role.description}
                    </option>
                  ))}
                </select>
                {errors.role && (
                  <p className="mt-1 text-sm text-red-600">{errors.role.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Account Status
                </label>
                <div className="flex items-center">
                  <input
                    {...register('is_active')}
                    type="checkbox"
                    defaultChecked
                    className="toggle toggle-primary mr-3"
                  />
                  <span className="text-sm text-gray-700">
                    Active (User can log in and access the system)
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Password */}
          <div className="border-t pt-6">
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <Lock className="h-5 w-5 mr-2" />
              Password
            </h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    {...register('password', { 
                      required: 'Password is required',
                      minLength: {
                        value: 6,
                        message: 'Password must be at least 6 characters'
                      }
                    })}
                    type="password"
                    className="input pl-10"
                    placeholder="Enter password"
                  />
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    {...register('confirmPassword', { 
                      required: 'Please confirm password',
                      validate: value => value === password || 'Passwords do not match'
                    })}
                    type="password"
                    className="input pl-10"
                    placeholder="Confirm password"
                  />
                </div>
                {errors.confirmPassword && (
                  <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
                )}
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
                  Create User
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Help section */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">User Role Permissions</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p><strong>Administrator:</strong> Full system access, user management, system configuration</p>
          <p><strong>Investigator:</strong> Case management, violation investigation, report generation</p>
          <p><strong>Regulator:</strong> View reports, analytics, and compliance data</p>
        </div>
      </div>
    </div>
  )
}
