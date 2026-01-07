import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { subtaskService } from '../services/api'
import { useAuthStore } from '../stores/auth'

export default function Dashboard() {
  const { user, isAuthenticated } = useAuthStore()

  const { data: claimedSubtasks, isLoading } = useQuery({
    queryKey: ['my-subtasks'],
    queryFn: () => subtaskService.list({ status: 'claimed' }),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) {
    return (
      <div className="card p-8 text-center">
        <p className="text-gray-600">Please connect your wallet to view your dashboard.</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="text-sm text-gray-500">Tasks Completed</div>
          <div className="text-2xl font-bold text-gray-900">{user?.tasks_completed || 0}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500">Active Claims</div>
          <div className="text-2xl font-bold text-gray-900">
            {claimedSubtasks?.subtasks?.length || 0}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500">Reputation</div>
          <div className="text-2xl font-bold text-gray-900">{user?.reputation_score || 0}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500">Tier</div>
          <div className="text-2xl font-bold text-primary-600 capitalize">
            {user?.reputation_tier || 'New'}
          </div>
        </div>
      </div>

      {/* Active Claims */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">My Active Claims</h2>
        
        {isLoading ? (
          <div className="card p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : claimedSubtasks?.subtasks?.length > 0 ? (
          <div className="space-y-4">
            {claimedSubtasks.subtasks.map((subtask: any) => (
              <div key={subtask.id} className="card p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{subtask.title}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="badge-gray">{subtask.subtask_type}</span>
                      <span className="badge-warning">{subtask.status}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="font-medium text-primary-600">
                        {parseFloat(subtask.budget_cngn).toLocaleString()} cNGN
                      </div>
                    </div>
                    <Link
                      to={`/tasks/${subtask.task_id}`}
                      className="btn-primary text-sm"
                    >
                      View Task
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card p-8 text-center">
            <p className="text-gray-500 mb-4">You haven't claimed any subtasks yet.</p>
            <Link to="/tasks" className="btn-primary">
              Browse Tasks
            </Link>
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Getting Started</h2>
        <div className="card p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                isAuthenticated ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
              }`}>
                {isAuthenticated ? '✓' : '1'}
              </div>
              <span className="text-gray-700">Connect your wallet</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                user?.name && user.name !== `User_${user.wallet_address.slice(0, 8)}` 
                  ? 'bg-green-100 text-green-600' 
                  : 'bg-gray-100 text-gray-400'
              }`}>
                {user?.name && user.name !== `User_${user.wallet_address.slice(0, 8)}` ? '✓' : '2'}
              </div>
              <span className="text-gray-700">Complete your profile</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                (claimedSubtasks?.subtasks?.length || 0) > 0
                  ? 'bg-green-100 text-green-600' 
                  : 'bg-gray-100 text-gray-400'
              }`}>
                {(claimedSubtasks?.subtasks?.length || 0) > 0 ? '✓' : '3'}
              </div>
              <span className="text-gray-700">Claim your first subtask</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                (user?.tasks_completed || 0) > 0
                  ? 'bg-green-100 text-green-600' 
                  : 'bg-gray-100 text-gray-400'
              }`}>
                {(user?.tasks_completed || 0) > 0 ? '✓' : '4'}
              </div>
              <span className="text-gray-700">Submit work and get paid</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
