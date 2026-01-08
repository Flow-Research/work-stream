import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { subtaskService } from '../services/api'
import { useAuthStore } from '../stores/auth'

export default function Dashboard() {
  const { user, isAuthenticated } = useAuthStore()

  const { data: claimedSubtasks, isLoading: claimedLoading } = useQuery({
    queryKey: ['my-subtasks', 'claimed'],
    queryFn: () => subtaskService.list({ status: 'claimed' }),
    enabled: isAuthenticated,
  })

  const { data: submittedSubtasks, isLoading: submittedLoading } = useQuery({
    queryKey: ['my-subtasks', 'submitted'],
    queryFn: () => subtaskService.list({ status: 'submitted' }),
    enabled: isAuthenticated,
  })

  const { data: approvedSubtasks } = useQuery({
    queryKey: ['my-subtasks', 'approved'],
    queryFn: () => subtaskService.list({ status: 'approved' }),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) {
    return (
      <div className="card p-8 text-center">
        <p className="text-gray-600">Please connect your wallet to view your dashboard.</p>
      </div>
    )
  }

  const totalEarnings = approvedSubtasks?.subtasks?.reduce(
    (sum: number, st: any) => sum + parseFloat(st.budget_cngn || '0'), 0
  ) || 0

  const pendingPayments = submittedSubtasks?.subtasks?.length || 0

  const allSubmissions = [
    ...(submittedSubtasks?.subtasks || []).map((s: any) => ({ ...s, displayStatus: 'pending' })),
    ...(approvedSubtasks?.subtasks || []).map((s: any) => ({ ...s, displayStatus: 'approved' })),
  ].sort((a, b) => new Date(b.claimed_at).getTime() - new Date(a.claimed_at).getTime())

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
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
          <div className="text-sm text-gray-500">Pending Review</div>
          <div className="text-2xl font-bold text-amber-600">{pendingPayments}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-gray-500">Total Earned</div>
          <div className="text-2xl font-bold text-green-600">₦{totalEarnings.toLocaleString()}</div>
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

      <div className="card p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Earnings Summary</h2>
        <div className="grid grid-cols-3 gap-6">
          <div>
            <div className="text-3xl font-bold text-green-600">₦{totalEarnings.toLocaleString()}</div>
            <div className="text-sm text-gray-500">Total Earned</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-amber-600">{pendingPayments}</div>
            <div className="text-sm text-gray-500">Pending Review</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-gray-400">₦0</div>
            <div className="text-sm text-gray-500">This Month</div>
          </div>
        </div>
        <div className="mt-4 h-2 bg-gray-100 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-green-400 to-green-600 rounded-full transition-all"
            style={{ width: `${Math.min((user?.tasks_completed || 0) * 10, 100)}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-2">Progress to next tier</p>
      </div>

      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">My Active Claims</h2>
        
        {claimedLoading ? (
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
                      <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-600">{subtask.subtask_type}</span>
                      <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 text-amber-700">{subtask.status}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="font-medium text-primary-600">
                        ₦{parseFloat(subtask.budget_cngn).toLocaleString()}
                      </div>
                    </div>
                    <Link
                      to={`/tasks/${subtask.task_id}`}
                      className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors"
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
            <Link to="/tasks" className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-colors inline-block">
              Browse Tasks
            </Link>
          </div>
        )}
      </div>

      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Submission History</h2>
        
        {submittedLoading ? (
          <div className="card p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : allSubmissions.length > 0 ? (
          <div className="card overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subtask</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {allSubmissions.slice(0, 10).map((submission: any) => (
                  <tr key={submission.id}>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{submission.title}</div>
                      <div className="text-sm text-gray-500">{submission.subtask_type}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                        submission.displayStatus === 'approved' 
                          ? 'bg-green-100 text-green-700' 
                          : submission.displayStatus === 'rejected'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-amber-100 text-amber-700'
                      }`}>
                        {submission.displayStatus}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-900">
                      ₦{parseFloat(submission.budget_cngn).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(submission.claimed_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <Link
                        to={`/tasks/${submission.task_id}`}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="card p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center text-3xl">📝</div>
            <p className="text-gray-500">No submissions yet. Complete your claimed tasks to see history here.</p>
          </div>
        )}
      </div>

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
