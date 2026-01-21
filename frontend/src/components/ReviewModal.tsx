import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { subtaskService } from '../services/api'
import { useDummyData, dummyDataTemplates } from '../hooks/useDummyData'

interface ReviewModalProps {
  isOpen: boolean
  onClose: () => void
  subtaskId: string
  taskTitle: string
  taskId?: string
  submission?: {
    content_summary: string
    artifact_ipfs_hash?: string
    artifact_type?: string
    submitted_at: string
  }
}

function ReviewModal({ isOpen, onClose, subtaskId, taskTitle: _taskTitle, submission: _submission }: ReviewModalProps) {
  const queryClient = useQueryClient()
  const [reviewNotes, setReviewNotes] = useState('')
  const [rating, setRating] = useState(5)

  // Use dummy data with keyboard shortcut
  useDummyData(
    'workReview',
    dummyDataTemplates.workReview,
    (data) => {
      setReviewNotes(data.review_notes)
      setRating(data.rating)
    },
    isOpen
  )

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setReviewNotes('')
      setRating(5)
    }
  }, [isOpen])

  const reviewMutation = useMutation({
    mutationFn: () => subtaskService.approve(subtaskId, reviewNotes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks'] })
      toast.success('Review submitted successfully!')
      handleClose()
    },
    onError: () => {
      toast.error('Failed to submit review. Please try again.')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!reviewNotes.trim()) {
      toast.error('Please provide review notes')
      return
    }
    reviewMutation.mutate()
  }

  const handleClose = () => {
    setReviewNotes('')
    setRating(5)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={handleClose} />
        
        <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg transform transition-all">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Review Work</h2>
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
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quality Rating
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className={`w-10 h-10 rounded-lg border-2 transition-all ${
                      rating >= star
                        ? 'border-yellow-400 bg-yellow-50 text-yellow-600'
                        : 'border-gray-200 text-gray-300'
                    }`}
                  >
                    {star}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Notes <span className="text-red-500">*</span>
              </label>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="Provide detailed feedback on the submitted work..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-shadow"
                rows={5}
                required
              />
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
                disabled={reviewMutation.isPending}
                className="flex-1 px-4 py-2.5 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {reviewMutation.isPending ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Reviewing...
                  </>
                ) : (
                  'Submit Review'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ReviewModal
