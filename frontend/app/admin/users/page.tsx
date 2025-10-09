'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Plus, Edit, Trash2, Search, User, Shield, Eye } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Link from 'next/link'

export default function UsersPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRole, setSelectedRole] = useState('')
  const queryClient = useQueryClient()

  // Mock data for users since we don't have a users API endpoint yet
  const { data: users, isLoading } = useQuery({
    queryKey: ['users', { search: searchTerm, role: selectedRole }],
    queryFn: async () => {
      // This would be replaced with actual API call when users endpoint is available
      return {
        results: [
          {
            id: 1,
            email: 'admin@example.com',
            name: 'Admin User',
            role: 'admin',
            is_active: true,
            created_at: '2024-01-01T00:00:00Z',
            last_login: '2024-01-15T10:30:00Z'
          },
          {
            id: 2,
            email: 'investigator@example.com',
            name: 'Investigator User',
            role: 'investigator',
            is_active: true,
            created_at: '2024-01-02T00:00:00Z',
            last_login: '2024-01-14T15:45:00Z'
          },
          {
            id: 3,
            email: 'regulator@example.com',
            name: 'Regulator User',
            role: 'regulator',
            is_active: true,
            created_at: '2024-01-03T00:00:00Z',
            last_login: '2024-01-13T09:20:00Z'
          }
        ],
        count: 3
      }
    },
  })

  const deleteUserMutation = useMutation({
    mutationFn: async (id: number) => {
      // This would be replaced with actual API call when users endpoint is available
      throw new Error('User deletion not implemented yet')
    },
    onSuccess: () => {
      toast.success('User deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete user')
    },
  })

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Are you sure you want to delete user "${name}"?`)) {
      deleteUserMutation.mutate(id)
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return <Shield className="h-4 w-4" />
      case 'investigator': return <User className="h-4 w-4" />
      case 'regulator': return <Eye className="h-4 w-4" />
      default: return <User className="h-4 w-4" />
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'badge-error'
      case 'investigator': return 'badge-info'
      case 'regulator': return 'badge-warning'
      default: return 'badge-neutral'
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
          <h1 className="text-2xl font-bold text-gray-900">Users Management</h1>
          <p className="text-gray-600">
            Manage system users and their roles
          </p>
        </div>
        <Link
          href="/admin/users/new"
          className="btn btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add User
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
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="input"
              >
                <option value="">All Roles</option>
                <option value="admin">Admin</option>
                <option value="investigator">Investigator</option>
                <option value="regulator">Regulator</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Users table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">
            Users ({users?.count || 0})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users?.results?.map((user: any) => (
                <tr key={user.id}>
                  <td>
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8">
                        <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                          {getRoleIcon(user.role)}
                        </div>
                      </div>
                      <div className="ml-3">
                        <p className="font-medium text-gray-900">{user.name}</p>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="text-gray-600">{user.email}</span>
                  </td>
                  <td>
                    <span className={`badge ${getRoleColor(user.role)} flex items-center w-fit`}>
                      {getRoleIcon(user.role)}
                      <span className="ml-1 capitalize">{user.role}</span>
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${user.is_active ? 'badge-success' : 'badge-warning'}`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="text-gray-600">
                    {user.last_login ? formatDate(user.last_login) : 'Never'}
                  </td>
                  <td className="text-gray-600">
                    {formatDate(user.created_at)}
                  </td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <Link
                        href={`/admin/users/${user.id}`}
                        className="p-1 text-gray-400 hover:text-blue-600"
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </Link>
                      <Link
                        href={`/admin/users/${user.id}/edit`}
                        className="p-1 text-gray-400 hover:text-green-600"
                        title="Edit User"
                      >
                        <Edit className="h-4 w-4" />
                      </Link>
                      <button
                        onClick={() => handleDelete(user.id, user.name)}
                        className="p-1 text-gray-400 hover:text-red-600"
                        disabled={deleteUserMutation.isPending}
                        title="Delete User"
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

        {users?.results?.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No users found</p>
            <Link
              href="/admin/users/new"
              className="btn btn-primary mt-4"
            >
              Add your first user
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
