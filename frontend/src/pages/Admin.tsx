import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminService } from '../services/api'
import { useAuthStore } from '../stores/auth'

export default function Admin() {
  const { user, isAuthenticated } = useAuthStore()
  const [activeTab, setActiveTab] = useState<'users' | 'disputes'>('users')

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminService.listUsers(),
    enabled: isAuthenticated && user?.is_admin,
  })

  const { data: disputes, isLoading: disputesLoading } = useQuery({
    queryKey: ['admin-disputes'],
    queryFn: () => adminService.listDisputes(),
    enabled: isAuthenticated && user?.is_admin,
  })

  if (!isAuthenticated || !user?.is_admin) {
    return (
      <div className="card p-8 text-center">
        <p className="text-gray-600">You don't have permission to access this page.</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="text-sm text-gray-500">Total Users</div>
          <div className="text-2xl font-bold text-gray-900">{users?.total || 0}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500">Open Disputes</div>
          <div className="text-2xl font-bold text-gray-900">
            {disputes?.disputes?.filter((d: any) => d.status === 'open').length || 0}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500">Pending Verifications</div>
          <div className="text-2xl font-bold text-gray-900">
            {users?.users?.filter((u: any) => !u.id_verified).length || 0}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('users')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Users
          </button>
          <button
            onClick={() => setActiveTab('disputes')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'disputes'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Disputes
          </button>
        </nav>
      </div>

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div>
          {usersLoading ? (
            <div className="card p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            </div>
          ) : (
            <div className="card overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Wallet
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tasks
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users?.users?.map((u: any) => (
                    <tr key={u.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{u.name}</div>
                        <div className="text-sm text-gray-500">{u.country}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {u.wallet_address.slice(0, 6)}...{u.wallet_address.slice(-4)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex space-x-2">
                          {u.id_verified ? (
                            <span className="badge-success">Verified</span>
                          ) : (
                            <span className="badge-warning">Unverified</span>
                          )}
                          {u.is_banned && <span className="badge-error">Banned</span>}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {u.tasks_completed}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {!u.id_verified && (
                          <button className="text-primary-600 hover:text-primary-800 mr-4">
                            Verify
                          </button>
                        )}
                        {!u.is_banned ? (
                          <button className="text-red-600 hover:text-red-800">
                            Ban
                          </button>
                        ) : (
                          <button className="text-green-600 hover:text-green-800">
                            Unban
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Disputes Tab */}
      {activeTab === 'disputes' && (
        <div>
          {disputesLoading ? (
            <div className="card p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            </div>
          ) : disputes?.disputes?.length > 0 ? (
            <div className="space-y-4">
              {disputes.disputes.map((dispute: any) => (
                <div key={dispute.id} className="card p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className={dispute.status === 'open' ? 'badge-error' : 'badge-success'}>
                          {dispute.status}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(dispute.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="mt-2 text-gray-700">{dispute.reason}</p>
                    </div>
                    {dispute.status === 'open' && (
                      <button className="btn-primary">Resolve</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card p-8 text-center">
              <p className="text-gray-500">No disputes found.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
