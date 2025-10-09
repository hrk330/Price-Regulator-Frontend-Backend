'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { productsApi } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Save, ArrowLeft, Package, DollarSign, Tag, FileText } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

interface ProductForm {
  name: string
  category: string
  description: string
  regulated_price: number
  market_price: number
  unit: string
  is_active: boolean
}

export default function NewProductPage() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<ProductForm>()

  const onSubmit = async (data: ProductForm) => {
    setIsLoading(true)
    try {
      await productsApi.create(data)
      toast.success('Product created successfully')
      router.push('/admin/products')
    } catch (error) {
      toast.error('Failed to create product')
    } finally {
      setIsLoading(false)
    }
  }

  const categories = [
    'Food & Beverages',
    'Medicine & Healthcare',
    'Fuel & Energy',
    'Transportation',
    'Housing & Utilities',
    'Education',
    'Clothing & Textiles',
    'Electronics',
    'Other'
  ]

  const units = [
    'kg',
    'liter',
    'piece',
    'pack',
    'box',
    'bottle',
    'can',
    'bag',
    'meter',
    'other'
  ]

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Link
            href="/admin/products"
            className="btn btn-outline btn-sm mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Products
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Add New Product</h1>
            <p className="text-gray-600 mt-1">
              Create a new regulated product for price monitoring
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Product Information</h3>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product Name *
              </label>
              <div className="relative">
                <Package className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('name', { required: 'Product name is required' })}
                  type="text"
                  className="input pl-10"
                  placeholder="Enter product name"
                />
              </div>
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <select
                {...register('category', { required: 'Category is required' })}
                className="input"
              >
                <option value="">Select category</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
              {errors.category && (
                <p className="mt-1 text-sm text-red-600">{errors.category.message}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <div className="relative">
              <FileText className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <textarea
                {...register('description')}
                rows={3}
                className="input pl-10"
                placeholder="Enter product description"
              />
            </div>
          </div>

          {/* Pricing Information */}
          <div className="border-t pt-6">
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <DollarSign className="h-5 w-5 mr-2" />
              Pricing Information
            </h4>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Regulated Price *
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    {...register('regulated_price', { 
                      required: 'Regulated price is required',
                      min: { value: 0, message: 'Price must be positive' }
                    })}
                    type="number"
                    step="0.01"
                    className="input pl-10"
                    placeholder="0.00"
                  />
                </div>
                {errors.regulated_price && (
                  <p className="mt-1 text-sm text-red-600">{errors.regulated_price.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Market Price *
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    {...register('market_price', { 
                      required: 'Market price is required',
                      min: { value: 0, message: 'Price must be positive' }
                    })}
                    type="number"
                    step="0.01"
                    className="input pl-10"
                    placeholder="0.00"
                  />
                </div>
                {errors.market_price && (
                  <p className="mt-1 text-sm text-red-600">{errors.market_price.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Unit *
                </label>
                <div className="relative">
                  <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <select
                    {...register('unit', { required: 'Unit is required' })}
                    className="input pl-10"
                  >
                    <option value="">Select unit</option>
                    {units.map((unit) => (
                      <option key={unit} value={unit}>
                        {unit}
                      </option>
                    ))}
                  </select>
                </div>
                {errors.unit && (
                  <p className="mt-1 text-sm text-red-600">{errors.unit.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Status */}
          <div className="border-t pt-6">
            <div className="flex items-center">
              <input
                {...register('is_active')}
                type="checkbox"
                defaultChecked
                className="toggle toggle-primary mr-3"
              />
              <label className="text-sm font-medium text-gray-700">
                Active (Product will be monitored for price violations)
              </label>
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
                  Create Product
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Help section */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">Tips for Adding Products</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Use clear, descriptive product names that are easily identifiable</p>
          <p>• Select the most appropriate category for better organization</p>
          <p>• Ensure regulated and market prices are accurate and up-to-date</p>
          <p>• Choose the correct unit of measurement for the product</p>
          <p>• Only active products will be monitored for price violations</p>
        </div>
      </div>
    </div>
  )
}
