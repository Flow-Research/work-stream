import { useState, useCallback } from 'react'
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

interface EditableSubtask extends Subtask {
  isEditing?: boolean
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
  const [subtasks, setSubtasks] = useState<EditableSubtask[]>([])
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
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

  // Update a subtask field
  const updateSubtask = useCallback((index: number, field: keyof Subtask, value: string | number | string[]) => {
    setSubtasks(prev => prev.map((st, i) =>
      i === index ? { ...st, [field]: value } : st
    ))
  }, [])

  // Toggle edit mode for a subtask
  const toggleEdit = useCallback((index: number) => {
    setEditingIndex(prev => prev === index ? null : index)
    setExpandedIndex(index)
  }, [])

  const handleClose = () => {
    setSubtasks([])
    setExpandedIndex(null)
    setEditingIndex(null)
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
                  const isEditing = editingIndex === index

                  return (
                    <div key={index} className={`border rounded-xl overflow-hidden ${isEditing ? 'border-primary-300 ring-2 ring-primary-100' : 'border-gray-200'}`}>
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
                              {isEditing && (
                                <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-700">
                                  Editing
                                </span>
                              )}
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
                          {/* Edit Toggle Button */}
                          <div className="flex justify-end mb-3">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                toggleEdit(index)
                              }}
                              className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors ${
                                isEditing
                                  ? 'bg-primary-500 text-white hover:bg-primary-600'
                                  : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                              }`}
                            >
                              {isEditing ? '✓ Done Editing' : '✏️ Edit'}
                            </button>
                          </div>

                          {isEditing ? (
                            /* Edit Mode */
                            <div className="space-y-4">
                              <div>
                                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Title</label>
                                <input
                                  type="text"
                                  value={subtask.title}
                                  onChange={(e) => updateSubtask(index, 'title', e.target.value)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                />
                              </div>

                              <div>
                                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Description</label>
                                <textarea
                                  value={subtask.description}
                                  onChange={(e) => updateSubtask(index, 'description', e.target.value)}
                                  rows={3}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                />
                              </div>

                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Budget (CNGN)</label>
                                  <input
                                    type="number"
                                    value={subtask.budget_cngn}
                                    onChange={(e) => updateSubtask(index, 'budget_cngn', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                  />
                                </div>
                                <div>
                                  <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Est. Hours</label>
                                  <input
                                    type="number"
                                    value={subtask.estimated_hours}
                                    onChange={(e) => updateSubtask(index, 'estimated_hours', parseFloat(e.target.value) || 0)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                  />
                                </div>
                              </div>

                              <div>
                                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                                  Subtask Type
                                </label>
                                <select
                                  value={subtask.subtask_type}
                                  onChange={(e) => updateSubtask(index, 'subtask_type', e.target.value)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                >
                                  <option value="discovery">🔍 Discovery</option>
                                  <option value="extraction">⛏️ Extraction</option>
                                  <option value="mapping">🗺️ Mapping</option>
                                  <option value="assembly">🔧 Assembly</option>
                                  <option value="narrative">✍️ Narrative</option>
                                </select>
                              </div>

                              {subtask.acceptance_criteria && (
                                <div>
                                  <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                                    Acceptance Criteria (one per line)
                                  </label>
                                  <textarea
                                    value={subtask.acceptance_criteria.join('\n')}
                                    onChange={(e) => updateSubtask(index, 'acceptance_criteria', e.target.value.split('\n').filter(c => c.trim()))}
                                    rows={3}
                                    placeholder="Each line becomes a criterion"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                  />
                                </div>
                              )}
                            </div>
                          ) : (
                            /* View Mode */
                            <>
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
                            </>
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
