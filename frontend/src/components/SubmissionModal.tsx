import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { subtaskService } from '../services/api'
import { useDummyData, dummyDataTemplates } from '../hooks/useDummyData'

interface SubmissionModalProps {
  isOpen: boolean
  onClose: () => void
  subtaskId: string
  taskTitle?: string
  taskId?: string
}

interface Artifact {
  title: string
  description: string
  type: string
}

function SubmissionModal({ isOpen, onClose, subtaskId, taskTitle }: SubmissionModalProps) {
  const queryClient = useQueryClient()
  const [contentSummary, setContentSummary] = useState('')
  const [artifacts, setArtifacts] = useState<Artifact[]>([])
  const [newArtifact, setNewArtifact] = useState({ title: '', description: '', type: 'file' })

  // Use dummy data with keyboard shortcut
  useDummyData(
    'workSubmission',
    dummyDataTemplates.workSubmission,
    (data) => {
      setContentSummary(data.content_summary)
      setArtifacts(data.artifacts)
    },
    isOpen
  )

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setContentSummary('')
      setArtifacts([])
      setNewArtifact({ title: '', description: '', type: 'file' })
    }
  }, [isOpen])

  const submitMutation = useMutation({
    mutationFn: () => subtaskService.submit(subtaskId, contentSummary),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks'] })
      toast.success('Work submitted successfully!')
      handleClose()
    },
    onError: () => {
      toast.error('Failed to submit work. Please try again.')
    },
  })

  const handleAddArtifact = () => {
    if (newArtifact.title.trim()) {
      setArtifacts([...artifacts, { ...newArtifact }])
      setNewArtifact({ title: '', description: '', type: 'file' })
    }
  }

  const handleRemoveArtifact = (index: number) => {
    setArtifacts(artifacts.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!contentSummary.trim()) {
      toast.error('Please provide a summary of your work')
      return
    }
    submitMutation.mutate()
  }

  const handleClose = () => {
    setContentSummary('')
    setArtifacts([])
    setNewArtifact({ title: '', description: '', type: 'file' })
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={handleClose} />
        
        <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl transform transition-all max-h-[90vh] overflow-y-auto">
          <div className="px-6 py-4 border-b border-gray-200 sticky top-0 bg-white z-10">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Submit Work</h2>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-md">
                  ⌨️ Cmd/Ctrl + D for dummy data
                </span>
                <button onClick={handleClose} className="text-gray-400 hover:text-gray-600 transition-colors">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-5">
            {taskTitle && (
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h3 className="font-medium text-gray-900 mb-1">{taskTitle}</h3>
                <p className="text-sm text-gray-600">Submit your completed work for review.</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Work Summary <span className="text-red-500">*</span>
              </label>
              <textarea
                value={contentSummary}
                onChange={(e) => setContentSummary(e.target.value)}
                placeholder="Describe what you accomplished..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-shadow"
                rows={4}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Artifacts</label>
              {artifacts.length > 0 && (
                <div className="space-y-2 mb-3">
                  {artifacts.map((artifact, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                      <div>
                        <p className="font-medium text-gray-900">{artifact.title}</p>
                        <p className="text-sm text-gray-600">{artifact.description}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveArtifact(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  value={newArtifact.title}
                  onChange={(e) => setNewArtifact({ ...newArtifact, title: e.target.value })}
                  placeholder="Artifact title"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <select
                  value={newArtifact.type}
                  onChange={(e) => setNewArtifact({ ...newArtifact, type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="file">File</option>
                  <option value="dataset">Dataset</option>
                  <option value="report">Report</option>
                  <option value="image">Image</option>
                </select>
              </div>
              <textarea
                value={newArtifact.description}
                onChange={(e) => setNewArtifact({ ...newArtifact, description: e.target.value })}
                placeholder="Artifact description"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none mt-2"
                rows={2}
              />
              <button
                type="button"
                onClick={handleAddArtifact}
                className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors mt-2"
              >
                + Add Artifact
              </button>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitMutation.isPending}
                className="flex-1 px-4 py-2.5 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {submitMutation.isPending ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Submitting...
                  </>
                ) : (
                  'Submit Work'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default SubmissionModal
