import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminService } from '../services/api'
import { useAuthStore } from '../stores/auth'
import toast from 'react-hot-toast'

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)
  
  useState(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  })
  
  return debouncedValue
}

export default function Admin() {
  const { user, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'users' | 'disputes'>('users')
  const [searchQuery, setSearchQuery] = useState('')
  const [userFilter, setUserFilter] = useState<'all' | 'verified' | 'unverified' | 'banned'>('all')
  const [disputeFilter, setDisputeFilter] = useState<'all' | 'open' | 'resolved'>('all')
  const [banModalUser, setBanModalUser] = useState<{ id: string; name: string } | null>(null)
  const [banReason, setBanReason] = useState('')
  const [resolveModalDispute, setResolveModalDispute] = useState<any | null>(null)
  const [resolution, setResolution] = useState('')
  const [resolutionType, setResolutionType] = useState<'worker' | 'client' | 'split'>('worker')

  const debouncedSearch = useDebounce(searchQuery, 300)

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

  const verifyMutation = useMutation({
    mutationFn: (userId: string) => adminService.verifyUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      toast.success('User verified successfully')
    },
    onError: () => toast.error('Failed to verify user'),
  })

  const banMutation = useMutation({
    mutationFn: ({ userId, reason }: { userId: string; reason: string }) => 
      adminService.banUser(userId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      toast.success('User banned successfully')
      setBanModalUser(null)
      setBanReason('')
    },
    onError: () => toast.error('Failed to ban user'),
  })

  const resolveMutation = useMutation({
    mutationFn: ({ disputeId, winnerId, resolution }: { disputeId: string; winnerId: string; resolution: string }) =>
      adminService.resolveDispute(disputeId, winnerId, resolution),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-disputes'] })
      toast.success('Dispute resolved successfully')
      setResolveModalDispute(null)
      setResolution('')
    },
    onError: () => toast.error('Failed to resolve dispute'),
  })

  const filteredUsers = useMemo(() => {
    if (!users?.users) return []
    return users.users.filter((u: any) => {
      const matchesSearch = !debouncedSearch || 
        u.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        u.wallet_address.toLowerCase().includes(debouncedSearch.toLowerCase())
      
      const matchesFilter = 
        userFilter === 'all' ||
        (userFilter === 'verified' && u.id_verified) ||
        (userFilter === 'unverified' && !u.id_verified) ||
        (userFilter === 'banned' && u.is_banned)
      
      return matchesSearch && matchesFilter
    })
  }, [users?.users, debouncedSearch, userFilter])

  const filteredDisputes = useMemo(() => {
    if (!disputes?.disputes) return []
    return disputes.disputes.filter((d: any) => {
      return disputeFilter === 'all' || d.status === disputeFilter
    })
  }, [disputes?.disputes, disputeFilter])

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

      {activeTab === 'users' && (
        <div>
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search by name or wallet..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <select
              value={userFilter}
              onChange={(e) => setUserFilter(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Users</option>
              <option value="verified">Verified</option>
              <option value="unverified">Unverified</option>
              <option value="banned">Banned</option>
            </select>
          </div>

          {usersLoading ? (
            <div className="card p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            </div>
          ) : (
            <div className="card overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Wallet</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tasks</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUsers.map((u: any) => (
                    <tr key={u.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{u.name}</div>
                        <div className="text-sm text-gray-500">{u.country}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                        {u.wallet_address.slice(0, 6)}...{u.wallet_address.slice(-4)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex space-x-2">
                          {u.id_verified ? (
                            <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">Verified</span>
                          ) : (
                            <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-700">Unverified</span>
                          )}
                          {u.is_banned && <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700">Banned</span>}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{u.tasks_completed}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        {!u.id_verified && (
                          <button
                            onClick={() => verifyMutation.mutate(u.id)}
                            disabled={verifyMutation.isPending}
                            className="text-primary-600 hover:text-primary-800 font-medium disabled:opacity-50"
                          >
                            {verifyMutation.isPending ? '...' : 'Verify'}
                          </button>
                        )}
                        {!u.is_banned ? (
                          <button
                            onClick={() => setBanModalUser({ id: u.id, name: u.name })}
                            className="text-red-600 hover:text-red-800 font-medium"
                          >
                            Ban
                          </button>
                        ) : (
                          <button
                            onClick={() => verifyMutation.mutate(u.id)}
                            className="text-green-600 hover:text-green-800 font-medium"
                          >
                            Unban
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredUsers.length === 0 && (
                <div className="p-8 text-center text-gray-500">No users found</div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'disputes' && (
        <div>
          <div className="mb-4">
            <select
              value={disputeFilter}
              onChange={(e) => setDisputeFilter(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Disputes</option>
              <option value="open">Open</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          {disputesLoading ? (
            <div className="card p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            </div>
          ) : filteredDisputes.length > 0 ? (
            <div className="space-y-4">
              {filteredDisputes.map((dispute: any) => (
                <div key={dispute.id} className="card p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                          dispute.status === 'open' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                        }`}>
                          {dispute.status}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(dispute.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2">{dispute.reason}</p>
                      <p className="text-sm text-gray-500">
                        Raised by: {dispute.raised_by?.slice(0, 8)}...
                      </p>
                    </div>
                    {dispute.status === 'open' && (
                      <button
                        onClick={() => setResolveModalDispute(dispute)}
                        className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors"
                      >
                        Resolve
                      </button>
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

      {banModalUser && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setBanModalUser(null)} />
            <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Ban User: {banModalUser.name}</h3>
              <textarea
                value={banReason}
                onChange={(e) => setBanReason(e.target.value)}
                placeholder="Reason for banning (required)..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                rows={3}
              />
              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => setBanModalUser(null)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => banMutation.mutate({ userId: banModalUser.id, reason: banReason })}
                  disabled={!banReason.trim() || banMutation.isPending}
                  className="flex-1 px-4 py-2 bg-red-500 hover:bg-red-600 text-white font-medium rounded-xl disabled:opacity-50"
                >
                  {banMutation.isPending ? 'Banning...' : 'Confirm Ban'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {resolveModalDispute && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setResolveModalDispute(null)} />
            <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Resolve Dispute</h3>
              
              <div className="space-y-3 mb-4">
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="resolution"
                    checked={resolutionType === 'worker'}
                    onChange={() => setResolutionType('worker')}
                    className="text-primary-500"
                  />
                  <span>Award to Worker</span>
                </label>
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="resolution"
                    checked={resolutionType === 'client'}
                    onChange={() => setResolutionType('client')}
                    className="text-primary-500"
                  />
                  <span>Award to Client</span>
                </label>
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="resolution"
                    checked={resolutionType === 'split'}
                    onChange={() => setResolutionType('split')}
                    className="text-primary-500"
                  />
                  <span>Split</span>
                </label>
              </div>

              <textarea
                value={resolution}
                onChange={(e) => setResolution(e.target.value)}
                placeholder="Resolution notes (required)..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                rows={3}
              />
              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => setResolveModalDispute(null)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => resolveMutation.mutate({
                    disputeId: resolveModalDispute.id,
                    winnerId: resolutionType === 'worker' ? resolveModalDispute.raised_by : resolveModalDispute.raised_by,
                    resolution: `${resolutionType}: ${resolution}`,
                  })}
                  disabled={!resolution.trim() || resolveMutation.isPending}
                  className="flex-1 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl disabled:opacity-50"
                >
                  {resolveMutation.isPending ? 'Resolving...' : 'Confirm'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
