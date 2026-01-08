import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { taskService } from '../services/api'

interface Subtask {
  title: string
  description: string
  subtask_type: 'discovery' | 'extraction' | 'mapping' | 'assembly' | 'narrative'
  budget_cngn: string
  estimated_hours: number
  acceptance_criteria?: string[]
  deliverables?: Array<{ title: string; type: string; required: boolean }>
}

interface DecomposeTaskModalProps {
  isOpen: boolean
  onClose: () => void
  taskId: string
  taskTitle: string
  researchQuestion: string
  onSuccess?: () => void
}

const typeColors: Record<string, { bg: string; text: string }> = {
  discovery: { bg: 'bg-blue-100', text: 'text-blue-700' },
  extraction: { bg: 'bg-purple-100', text: 'text-purple-700' },
  mapping: { bg: 'bg-cyan-100', text: 'text-cyan-700' },
  assembly: { bg: 'bg-amber-100', text: 'text-amber-700' },
  narrative: { bg: 'bg-green-100', text: 'text-green-700' },
}

const typeIcons: Record<string, string> = {
  discovery: '🔍',
  extraction: '⛏️',
  mapping: '🗺️',
  assembly: '🔧',
  narrative: '✍️',
}

export default function DecomposeTaskModal({
  isOpen,
  onClose,
  taskId,
  taskTitle,
  researchQuestion,
  onSuccess,
}: DecomposeTaskModalProps) {
  const queryClient = useQueryClient()
  const [subtasks, setSubtasks] = useState<Subtask[]>([])
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)
  const [hasGenerated, setHasGenerated] = useState(false)

  const decomposeMutation = useMutation({
    mutationFn: () => taskService.decompose(taskId),
    onSuccess: (data) => {
      setSubtasks(data.subtasks || [])
      setHasGenerated(true)
      toast.success('Subtasks generated successfully!')
    },
    onError: () => {
      toast.error('Failed to generate subtasks. Please try again.')
    },
  })

  const handleClose = () => {
    setSubtasks([])
    setExpandedIndex(null)
    setHasGenerated(false)
    onClose()
  }

  const handleConfirm = () => {
    queryClient.invalidateQueries({ queryKey: ['task', taskId] })
    toast.success('Subtasks saved!')
    handleClose()
    onSuccess?.()
  }

  const handleRegenerate = () => {
    setSubtasks([])
    setExpandedIndex(null)
    decomposeMutation.mutate()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={handleClose} />
        
        <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-3xl transform transition-all max-h-[90vh] overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">AI Task Decomposition</h2>
                <p className="text-sm text-gray-500 mt-1 truncate max-w-md">{taskTitle}</p>
              </div>
              <button onClick={handleClose} className="text-gray-400 hover:text-gray-600 transition-colors">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6">
            {!hasGenerated && !decomposeMutation.isPending && (
              <div className="text-center py-8">
                <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-4xl">🤖</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready to Decompose</h3>
                <p className="text-gray-600 mb-2 max-w-md mx-auto">
                  AI will analyze your research question and break it down into actionable subtasks.
                </p>
                <div className="bg-blue-50 rounded-xl p-4 mb-6 text-left max-w-md mx-auto">
                  <p className="text-sm text-blue-800 font-medium">Research Question:</p>
                  <p className="text-sm text-blue-700 mt-1">{researchQuestion}</p>
                </div>
                <button
                  onClick={() => decomposeMutation.mutate()}
                  className="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl transition-colors"
                >
                  Generate Subtasks
                </button>
              </div>
            )}

            {decomposeMutation.isPending && (
              <div className="text-center py-12">
                <div className="relative w-20 h-20 mx-auto mb-4">
                  <div className="absolute inset-0 rounded-full border-4 border-primary-200"></div>
                  <div className="absolute inset-0 rounded-full border-4 border-primary-500 border-t-transparent animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl animate-pulse">🧠</span>
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AI is analyzing your task...</h3>
                <p className="text-gray-500 animate-pulse">This may take 10-30 seconds</p>
              </div>
            )}

            {hasGenerated && subtasks.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                    Generated Subtasks ({subtasks.length})
                  </h3>
                  <div className="text-sm text-gray-500">
                    Total: ₦{subtasks.reduce((sum, st) => sum + parseFloat(st.budget_cngn || '0'), 0).toLocaleString()}
                  </div>
                </div>

                {subtasks.map((subtask, index) => {
                  const colors = typeColors[subtask.subtask_type] || typeColors.discovery
                  const isExpanded = expandedIndex === index
                  
                  return (
                    <div key={index} className="border border-gray-200 rounded-xl overflow-hidden">
                      <div
                        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                        onClick={() => setExpandedIndex(isExpanded ? null : index)}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-xl">{typeIcons[subtask.subtask_type]}</span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <h4 className="font-medium text-gray-900">{subtask.title}</h4>
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
                                {subtask.subtask_type}
                              </span>
                            </div>
                            <p className="text-sm text-gray-500 truncate mt-0.5">{subtask.description}</p>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <div className="font-semibold text-gray-900">₦{parseFloat(subtask.budget_cngn).toLocaleString()}</div>
                            <div className="text-xs text-gray-500">{subtask.estimated_hours}h</div>
                          </div>
                          <svg className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </div>
                      </div>

                      {isExpanded && (
                        <div className="px-4 pb-4 pt-2 border-t border-gray-100 bg-gray-50">
                          <p className="text-sm text-gray-700 mb-3">{subtask.description}</p>
                          
                          {subtask.acceptance_criteria && subtask.acceptance_criteria.length > 0 && (
                            <div className="mb-3">
                              <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Acceptance Criteria</h5>
                              <ul className="space-y-1">
                                {subtask.acceptance_criteria.map((criterion, i) => (
                                  <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                                    <span className="text-green-500 mt-0.5">✓</span>
                                    {criterion}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {subtask.deliverables && subtask.deliverables.length > 0 && (
                            <div>
                              <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Deliverables</h5>
                              <div className="flex flex-wrap gap-2">
                                {subtask.deliverables.map((d, i) => (
                                  <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-white border border-gray-200 rounded-lg text-xs">
                                    {d.title}
                                    {d.required && <span className="text-red-500">*</span>}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}

            {hasGenerated && subtasks.length === 0 && (
              <div className="text-center py-8">
                <p className="text-gray-500">No subtasks were generated. Try again.</p>
              </div>
            )}
          </div>

          {hasGenerated && (
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-3">
              <button
                onClick={handleClose}
                className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-100 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleRegenerate}
                disabled={decomposeMutation.isPending}
                className="px-4 py-2.5 border border-primary-300 text-primary-700 font-medium rounded-xl hover:bg-primary-50 transition-colors disabled:opacity-50"
              >
                Regenerate
              </button>
              <button
                onClick={handleConfirm}
                className="flex-1 px-4 py-2.5 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl transition-colors"
              >
                Confirm & Save
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
