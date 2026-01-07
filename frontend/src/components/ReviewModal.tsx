import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { subtaskService } from '../services/api'

interface ReviewModalProps {
  isOpen: boolean
  onClose: () => void
  subtaskId: string
  subtaskTitle: string
  taskId: string
  submission?: {
    content_summary: string
    artifact_ipfs_hash?: string
    artifact_type?: string
    submitted_at: string
  }
}

export default function ReviewModal({
  isOpen,
  onClose,
  subtaskId,
  subtaskTitle,
  taskId,
  submission,
}: ReviewModalProps) {
  const [reviewNotes, setReviewNotes] = useState('')
  const [action, setAction] = useState<'approve' | 'reject' | null>(null)
  const queryClient = useQueryClient()

  const approveMutation = useMutation({
    mutationFn: () => subtaskService.approve(subtaskId, reviewNotes || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', taskId] })
      toast.success('Submission approved!')
      handleClose()
    },
    onError: () => {
      toast.error('Failed to approve submission')
    },
  })

  const rejectMutation = useMutation({
    mutationFn: () => subtaskService.reject(subtaskId, reviewNotes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', taskId] })
      toast.success('Submission rejected')
      handleClose()
    },
    onError: () => {
      toast.error('Failed to reject submission')
    },
  })

  const handleClose = () => {
    setReviewNotes('')
    setAction(null)
    onClose()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (action === 'reject' && !reviewNotes.trim()) {
      toast.error('Please provide rejection reason')
      return
    }

    if (action === 'approve') {
      approveMutation.mutate()
    } else if (action === 'reject') {
      rejectMutation.mutate()
    }
  }

  const isLoading = approveMutation.isPending || rejectMutation.isPending

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div 
          className="fixed inset-0 bg-black/50 transition-opacity"
          onClick={handleClose}
        />
        
        <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg transform transition-all">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Review Submission</h2>
              <button
                onClick={handleClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-1">{subtaskTitle}</p>
          </div>

          <div className="p-6 space-y-5">
            {submission && (
              <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                <div>
                  <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Work Summary</h4>
                  <p className="text-gray-900">{submission.content_summary}</p>
                </div>
                
                {submission.artifact_ipfs_hash && (
                  <div>
                    <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Artifact</h4>
                    <a
                      href={`https://gateway.pinata.cloud/ipfs/${submission.artifact_ipfs_hash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      View {submission.artifact_type?.toUpperCase()} file
                    </a>
                  </div>
                )}

                <div>
                  <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Submitted</h4>
                  <p className="text-sm text-gray-600">
                    {new Date(submission.submitted_at).toLocaleString()}
                  </p>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review Notes {action === 'reject' && <span className="text-red-500">*</span>}
                </label>
                <textarea
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder={action === 'reject' ? 'Explain why this submission is being rejected...' : 'Optional feedback for the contributor...'}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-shadow"
                  rows={3}
                  required={action === 'reject'}
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setAction('reject')
                    if (reviewNotes.trim()) {
                      rejectMutation.mutate()
                    }
                  }}
                  disabled={isLoading}
                  className="flex-1 px-4 py-2.5 border-2 border-red-500 text-red-600 font-medium rounded-xl hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {rejectMutation.isPending ? (
                    <>
                      <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Rejecting...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Reject
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAction('approve')
                    approveMutation.mutate()
                  }}
                  disabled={isLoading}
                  className="flex-1 px-4 py-2.5 bg-green-500 hover:bg-green-600 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {approveMutation.isPending ? (
                    <>
                      <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Approving...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Approve
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
