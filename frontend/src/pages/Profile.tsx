import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const AVAILABLE_SKILLS = [
  'Research', 'Data Analysis', 'Writing', 'Literature Review',
  'Python', 'R', 'Statistics', 'Machine Learning', 'NLP',
  'Biology', 'Chemistry', 'Physics', 'Medicine', 'Economics',
  'Sociology', 'Psychology', 'History', 'Philosophy', 'Law'
]

const tierBadges: Record<string, { label: string; color: string }> = {
  new: { label: 'New Member', color: 'bg-gray-100 text-gray-700' },
  active: { label: 'Active', color: 'bg-blue-100 text-blue-700' },
  established: { label: 'Established', color: 'bg-purple-100 text-purple-700' },
  expert: { label: 'Expert', color: 'bg-amber-100 text-amber-700' },
}

export default function Profile() {
  const { user, isAuthenticated, setUser } = useAuthStore()
  const [isEditing, setIsEditing] = useState(false)
  const [name, setName] = useState(user?.name || '')
  const [bio, setBio] = useState(user?.bio || '')
  const [skills, setSkills] = useState<string[]>(user?.skills || [])
  const [skillDropdownOpen, setSkillDropdownOpen] = useState(false)
  const [skillSearch, setSkillSearch] = useState('')

  const updateMutation = useMutation({
    mutationFn: async (data: { name?: string; bio?: string; skills?: string[] }) => {
      const response = await api.patch('/users/me', data)
      return response.data
    },
    onSuccess: (data) => {
      setUser(data)
      setIsEditing(false)
      toast.success('Profile updated successfully!')
    },
    onError: () => {
      toast.error('Failed to update profile')
    },
  })

  if (!isAuthenticated || !user) {
    return (
      <div className="card p-8 text-center">
        <p className="text-gray-600">Please connect your wallet to view your profile.</p>
      </div>
    )
  }

  const tier = tierBadges[user.reputation_tier] || tierBadges.new

  const handleSave = () => {
    if (!name.trim()) {
      toast.error('Name is required')
      return
    }
    updateMutation.mutate({ name, bio, skills })
  }

  const handleCancel = () => {
    setName(user.name || '')
    setBio(user.bio || '')
    setSkills(user.skills || [])
    setIsEditing(false)
  }

  const addSkill = (skill: string) => {
    if (skills.length >= 10) {
      toast.error('Maximum 10 skills allowed')
      return
    }
    if (!skills.includes(skill)) {
      setSkills([...skills, skill])
    }
    setSkillDropdownOpen(false)
    setSkillSearch('')
  }

  const removeSkill = (skillToRemove: string) => {
    setSkills(skills.filter(s => s !== skillToRemove))
  }

  const filteredSkills = AVAILABLE_SKILLS.filter(
    s => s.toLowerCase().includes(skillSearch.toLowerCase()) && !skills.includes(s)
  )

  return (
    <div className="max-w-2xl mx-auto space-y-8">
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
              <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${tier.color}`}>{tier.label}</span>
              {user.id_verified && (
                <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">Verified</span>
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1 font-mono">
              {user.wallet_address.slice(0, 6)}...{user.wallet_address.slice(-4)}
            </p>
          </div>
        </div>
      </div>

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

      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Profile Details</h2>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors text-sm"
            >
              Edit
            </button>
          )}
        </div>

        {isEditing ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                placeholder="Tell us about yourself..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Skills ({skills.length}/10)
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {skills.map((skill) => (
                  <span key={skill} className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                    {skill}
                    <button onClick={() => removeSkill(skill)} className="hover:text-primary-900">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
              <div className="relative">
                <input
                  type="text"
                  value={skillSearch}
                  onChange={(e) => {
                    setSkillSearch(e.target.value)
                    setSkillDropdownOpen(true)
                  }}
                  onFocus={() => setSkillDropdownOpen(true)}
                  placeholder="Search and add skills..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                {skillDropdownOpen && filteredSkills.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto">
                    {filteredSkills.map((skill) => (
                      <button
                        key={skill}
                        onClick={() => addSkill(skill)}
                        className="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm"
                      >
                        {skill}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
              <input
                type="text"
                value={user.country}
                disabled
                className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 text-gray-500"
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={handleCancel}
                className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={updateMutation.isPending}
                className="flex-1 px-4 py-2.5 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {updateMutation.isPending ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>
          </div>
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
                    <span key={skill} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">{skill}</span>
                  ))
                ) : (
                  <p className="text-gray-500">No skills added</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {!user.id_verified && (
        <div className="card p-6 bg-yellow-50 border-yellow-200">
          <h2 className="text-lg font-semibold text-yellow-800 mb-2">
            Verify Your Identity
          </h2>
          <p className="text-yellow-700 mb-4">
            Verify your identity to unlock higher-paying tasks and build trust.
          </p>
          <button className="px-4 py-2 bg-yellow-600 text-white font-medium rounded-lg hover:bg-yellow-700 transition-colors">
            Start Verification
          </button>
        </div>
      )}
    </div>
  )
}
