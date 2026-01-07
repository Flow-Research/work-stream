import { useState } from 'react'
import { useAuthStore } from '../stores/auth'

const tierBadges: Record<string, { label: string; icon: string }> = {
  new: { label: 'New Member', icon: '' },
  active: { label: 'Active', icon: '' },
  established: { label: 'Established', icon: '' },
  expert: { label: 'Expert', icon: '' },
}

export default function Profile() {
  const { user, isAuthenticated } = useAuthStore()
  const [isEditing, setIsEditing] = useState(false)
  const [name, setName] = useState(user?.name || '')
  const [bio, setBio] = useState(user?.bio || '')

  if (!isAuthenticated || !user) {
    return (
      <div className="card p-8 text-center">
        <p className="text-gray-600">Please connect your wallet to view your profile.</p>
      </div>
    )
  }

  const tier = tierBadges[user.reputation_tier] || tierBadges.new

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Profile Header */}
      <div className="card p-6">
        <div className="flex items-center space-x-4">
          <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-3xl text-primary-600">
              {user.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{user.name}</h1>
            <div className="flex items-center space-x-2 mt-1">
              <span className="badge-info">{tier.label}</span>
              {user.id_verified && (
                <span className="badge-success">Verified</span>
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {user.wallet_address.slice(0, 6)}...{user.wallet_address.slice(-4)}
            </p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{user.tasks_completed}</div>
          <div className="text-sm text-gray-500">Tasks Completed</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{user.tasks_approved || 0}</div>
          <div className="text-sm text-gray-500">Tasks Approved</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{user.reputation_score || 0}</div>
          <div className="text-sm text-gray-500">Reputation Score</div>
        </div>
      </div>

      {/* Profile Details */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Profile Details</h2>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="btn-secondary text-sm"
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        {isEditing ? (
          <form className="space-y-4">
            <div>
              <label className="label">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label">Bio</label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={4}
                className="input"
                placeholder="Tell us about yourself..."
              />
            </div>
            <div>
              <label className="label">Country</label>
              <input
                type="text"
                value={user.country}
                disabled
                className="input bg-gray-50"
              />
            </div>
            <button type="submit" className="btn-primary">
              Save Changes
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Name</label>
              <p className="text-gray-900">{user.name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Bio</label>
              <p className="text-gray-900">{user.bio || 'No bio yet'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Country</label>
              <p className="text-gray-900">{user.country}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Skills</label>
              <div className="flex flex-wrap gap-2 mt-1">
                {user.skills && user.skills.length > 0 ? (
                  user.skills.map((skill) => (
                    <span key={skill} className="badge-gray">{skill}</span>
                  ))
                ) : (
                  <p className="text-gray-500">No skills added</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ID Verification */}
      {!user.id_verified && (
        <div className="card p-6 bg-yellow-50 border-yellow-200">
          <h2 className="text-lg font-semibold text-yellow-800 mb-2">
            Verify Your Identity
          </h2>
          <p className="text-yellow-700 mb-4">
            Verify your identity to unlock higher-paying tasks and build trust.
          </p>
          <button className="btn bg-yellow-600 text-white hover:bg-yellow-700">
            Start Verification
          </button>
        </div>
      )}
    </div>
  )
}
