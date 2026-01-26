import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { taskService, subtaskService } from '../services/api'
import { useAuthStore } from '../stores/auth'
import toast from 'react-hot-toast'
import SubmissionModal from '../components/SubmissionModal'
import ReviewModal from '../components/ReviewModal'
import FundTaskButton from '../components/FundTaskButton'
import DecomposeTaskModal from '../components/DecomposeTaskModal'
import CountdownTimer, { InlineCountdown } from '../components/CountdownTimer'
import type { SubtaskBrief, SubtaskStatus, SubtaskType, ReferenceItem, Subtask, DeliverableItem, TaskStatus, Task } from '../types'

const subtaskTypeLabels: Record<SubtaskType, string> = {
  discovery: 'Discovery',
  extraction: 'Extraction',
  mapping: 'Mapping',
  assembly: 'Assembly',
  narrative: 'Narrative',
}

const taskStatusLabels: Record<TaskStatus, string> = {
  draft: 'Pending',
  funded: 'Funded',
  decomposed: 'Decomposed',
  in_progress: 'In Progress',
  in_review: 'In Review',
  completed: 'Completed',
  cancelled: 'Cancelled',
  disputed: 'Disputed',
}

const subtaskStatusLabels: Record<SubtaskStatus, string> = {
  open: 'Open',
  claimed: 'Claimed',
  in_progress: 'In Progress',
  submitted: 'Submitted',
  approved: 'Approved',
  rejected: 'Rejected',
  disputed: 'Disputed',
}



export default function TaskDetail() {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const [expandedSubtask, setExpandedSubtask] = useState<string | null>(null)
  const [subtaskDetails, setSubtaskDetails] = useState<Record<string, Subtask>>({})
  const [submissionModal, setSubmissionModal] = useState<{ isOpen: boolean; subtaskId: string; taskTitle: string }>({
    isOpen: false,
    subtaskId: '',
    taskTitle: '',
  })
  const [reviewModal, setReviewModal] = useState<{
    isOpen: boolean
    subtaskId: string
    taskTitle: string
    submission?: {
      content_summary: string
      artifact_ipfs_hash?: string
      artifact_type?: string
      submitted_at: string
    }
  }>({
    isOpen: false,
    subtaskId: '',
    taskTitle: '',
  })
  const [showDecomposeModal, setShowDecomposeModal] = useState(false)

  const { data: task, isLoading, error } = useQuery<Task>({
    queryKey: ['task', taskId],
    queryFn: () => taskService.get(taskId!),
    enabled: !!taskId,
  })

  const claimMutation = useMutation({
    mutationFn: (subtaskId: string) => subtaskService.claim(subtaskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', taskId] })
      toast.success('Subtask claimed successfully!')
    },
    onError: () => {
      toast.error('Failed to claim subtask')
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !task) {
    return (
      <div className="text-center text-red-600">
        Task not found or error loading task.
      </div>
    )
  }

  const canClaim = isAuthenticated && ['funded', 'decomposed', 'in_progress'].includes(task.status)

  const toggleSubtask = async (subtaskId: string) => {
    if (expandedSubtask === subtaskId) {
      setExpandedSubtask(null)
      return
    }
    setExpandedSubtask(subtaskId)
    if (!subtaskDetails[subtaskId]) {
      try {
        const data = await subtaskService.get(subtaskId)
        setSubtaskDetails(prev => ({ ...prev, [subtaskId]: data }))
      } catch {
        toast.error('Failed to load subtask details')
      }
    }
  }

  const statusConfig: Record<string, { bg: string; text: string; dot: string }> = {
    draft: { bg: 'bg-gray-100', text: 'text-gray-700', dot: 'bg-gray-400' },
    funded: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-400' },
    decomposed: { bg: 'bg-purple-50', text: 'text-purple-700', dot: 'bg-purple-400' },
    in_progress: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-400' },
    in_review: { bg: 'bg-orange-50', text: 'text-orange-700', dot: 'bg-orange-400' },
    completed: { bg: 'bg-green-50', text: 'text-green-700', dot: 'bg-green-400' },
    cancelled: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-400' },
    disputed: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-400' },
  }

  const status = statusConfig[task.status] || statusConfig.draft

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center gap-2 text-sm">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-200 group"
        >
          <svg className="w-4 h-4 transform group-hover:-translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <span className="text-gray-300">/</span>
        <Link to="/tasks" className="text-gray-500 hover:text-primary-600 transition-colors">
          Tasks
        </Link>
        <span className="text-gray-300">/</span>
        <span className="text-primary-700 font-medium truncate max-w-xs">{task.title}</span>
      </nav>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="bg-primary-500 px-8 py-6">
          <div className="flex items-start justify-between">
            <div className="space-y-3">
              <h1 className="text-2xl font-bold text-white">{task.title}</h1>
              <div className="flex items-center gap-3 flex-wrap">
                <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${status.bg} ${status.text}`}>
                  <span className={`w-2 h-2 rounded-full ${status.dot}`}></span>
                  {taskStatusLabels[task.status]}
                </span>
                {task.skills_required?.map((skill: string) => (
                  <span key={skill} className="px-3 py-1 rounded-full text-sm font-medium bg-white/20 text-white">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            <div className="text-right bg-white/10 rounded-xl px-5 py-3 backdrop-blur-sm">
              <div className="text-3xl font-bold text-white">
                ₦{parseFloat(task.total_budget_cngn).toLocaleString()}
              </div>
              <div className="text-sm text-white/80">Total Budget</div>
            </div>
          </div>
          
          {task.status === 'draft' && (task.client_id === user?.id || user?.is_admin) && (
            <div className="mt-4 max-w-xs">
              <FundTaskButton
                taskId={taskId!}
                budgetCngn={task.total_budget_cngn}
                onSuccess={() => queryClient.invalidateQueries({ queryKey: ['task', taskId] })}
              />
            </div>
          )}
          
          {(task.status === 'funded' || task.status === 'decomposed') && 
           (!task.subtasks || task.subtasks.length === 0) && 
           (task.client_id === user?.id || user?.is_admin) && (
            <div className="mt-4">
              <button
                onClick={() => setShowDecomposeModal(true)}
                className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
              >
                <span>🤖</span>
                Decompose with AI
              </button>
            </div>
          )}
        </div>

        <div className="p-8 space-y-8">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
            <div className="flex items-start gap-3">
              <div>
                <h3 className="text-sm font-semibold text-blue-900 uppercase tracking-wide mb-2">Research Question</h3>
                <p className="text-lg text-blue-800 font-medium leading-relaxed">{task.research_question}</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {task.deadline && (
              <div className="bg-white rounded-xl p-4 border border-gray-200 cursor-pointer transition-all duration-300 hover:shadow-md hover:border-primary-200 hover:-translate-y-0.5 group">
                <div className="flex items-center gap-2 text-gray-500 text-sm mb-1 group-hover:text-primary-600 transition-colors">
                  <span>📅</span>
                  <span className="font-medium">Deadline</span>
                </div>
                <p className="text-gray-900 font-semibold group-hover:text-primary-700 transition-colors">
                  {new Date(task.deadline).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                </p>
              </div>
            )}
            <div
              className="bg-white rounded-xl p-4 border border-gray-200 cursor-pointer transition-all duration-300 hover:shadow-md hover:border-primary-200 hover:-translate-y-0.5 group"
              onClick={() => document.getElementById('subtasks-section')?.scrollIntoView({ behavior: 'smooth' })}
            >
              <div className="flex items-center gap-2 text-gray-500 text-sm mb-1 group-hover:text-primary-600 transition-colors">
                <span>📊</span>
                <span className="font-medium">Subtasks</span>
              </div>
              <p className="text-gray-900 font-semibold group-hover:text-primary-700 transition-colors">{task.subtasks?.length || 0} tasks</p>
            </div>
            <div className="bg-white rounded-xl p-4 border border-gray-200 cursor-default transition-all duration-300 hover:shadow-md hover:border-gray-300 group">
              <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
                <span>⏱️</span>
                <span className="font-medium">Created</span>
              </div>
              <p className="text-gray-900 font-semibold">
                {new Date(task.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </p>
            </div>
          </div>

          <hr />

          <div>
            <div className="flex items-center gap-2 mb-3">
              <h3 className="text-lg font-semibold text-gray-900">Description</h3>
            </div>
            <p className="text-gray-600 leading-relaxed">{task.description}</p>
          </div>

          {task.background_context && (
            <div className="bg-amber-50 rounded-xl p-6 border border-amber-100">
              <div className="flex items-start gap-3">
                <span className="text-xl">💡</span>
                <div>
                  <h3 className="text-sm font-semibold text-amber-900 uppercase tracking-wide mb-2">Background Context</h3>
                  <p className="text-amber-800 leading-relaxed">{task.background_context}</p>
                </div>
              </div>
            </div>
          )}

          {task.methodology_notes && (
            <div className="bg-emerald-50 rounded-xl p-6 border border-emerald-100">
              <div className="flex items-start gap-3">
                <span className="text-xl">🔬</span>
                <div>
                  <h3 className="text-sm font-semibold text-emerald-900 uppercase tracking-wide mb-2">Methodology</h3>
                  <p className="text-emerald-800 leading-relaxed">{task.methodology_notes}</p>
                </div>
              </div>
            </div>
          )}

          <hr />

          {task.expected_outcomes && task.expected_outcomes.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Expected Outcomes</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {task.expected_outcomes.map((outcome: string, idx: number) => (
                  <span 
                    key={idx} 
                    className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 text-green-800 rounded-lg border border-green-200 text-sm"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                    {outcome}
                  </span>
                ))}
              </div>
            </div>
          )}

          <hr />

          {task.references && task.references.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <h3 className="text-lg font-semibold text-gray-900">References</h3>
              </div>
              <div className="grid gap-3">
                {task.references.map((ref: ReferenceItem) => (
                  <a
                    key={ref.id}
                    href={ref.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-xl border border-gray-200 transition-all duration-200"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-10 h-10 rounded-lg bg-white border border-gray-200 flex items-center justify-center text-lg shadow-sm">
                        {ref.type === 'paper' ? '📄' : ref.type === 'dataset' ? '📊' : ref.type === 'document' ? '📝' : '🔗'}
                      </span>
                      <div>
                        <div className="font-medium text-gray-900 group-hover:text-primary-600 transition-colors">
                          {ref.title}
                        </div>
                        <div className="text-sm text-gray-500">{ref.type}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {ref.required && (
                        <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-md">Required</span>
                      )}
                      <span className="text-gray-400 group-hover:text-primary-600 transition-colors">→</span>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Subtasks */}
      <div id="subtasks-section" className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden scroll-mt-6">
        <div className="px-8 py-5 border-b border-gray-100 bg-gray-50/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📝</span>
              <h2 className="text-xl font-bold text-gray-900">Subtasks</h2>
              <span className="px-2.5 py-1 bg-gray-200 text-gray-700 text-sm font-medium rounded-full">
                {task.subtasks?.length || 0}
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-blue-400"></span> Open
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span> In Progress
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-400"></span> Approved
              </span>
            </div>
          </div>
        </div>
        
        {task.subtasks && task.subtasks.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {task.subtasks.map((subtask: SubtaskBrief, index: number) => {
              const details = subtaskDetails[subtask.id]
              const isExpanded = expandedSubtask === subtask.id
              const typeIcons: Record<SubtaskType, string> = {
                discovery: '🔍',
                extraction: '⛏️',
                mapping: '🗺️',
                assembly: '🔧',
                narrative: '✍️',
              }
              const statusStyles: Record<SubtaskStatus, { bg: string; text: string; dot: string }> = {
                open: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-400' },
                claimed: { bg: 'bg-purple-50', text: 'text-purple-700', dot: 'bg-purple-400' },
                in_progress: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-400' },
                submitted: { bg: 'bg-orange-50', text: 'text-orange-700', dot: 'bg-orange-400' },
                approved: { bg: 'bg-green-50', text: 'text-green-700', dot: 'bg-green-400' },
                rejected: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-400' },
                disputed: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-400' },
              }
              const statusStyle = statusStyles[subtask.status]
              
              return (
                <div key={subtask.id} className={`${isExpanded ? 'bg-slate-50' : 'hover:bg-gray-50'} transition-colors`}>
                  <div 
                    className="px-8 py-5 cursor-pointer"
                    onClick={() => toggleSubtask(subtask.id)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        <span className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-lg">
                          {typeIcons[subtask.subtask_type]}
                        </span>
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs font-semibold text-gray-600">
                          {index + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3">
                            <h3 className="font-semibold text-gray-900 truncate">{subtask.title}</h3>
                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusStyle.bg} ${statusStyle.text}`}>
                              <span className={`w-1.5 h-1.5 rounded-full ${statusStyle.dot}`}></span>
                              {subtaskStatusLabels[subtask.status]}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-0.5">{subtaskTypeLabels[subtask.subtask_type]}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        {/* Inline countdown for claimed/in_progress subtasks */}
                        {(subtask.status === 'claimed' || subtask.status === 'in_progress') && subtaskDetails[subtask.id] && (
                          <InlineCountdown
                            deadline={subtaskDetails[subtask.id].deadline}
                            claimedAt={subtaskDetails[subtask.id].claimed_at}
                            estimatedHours={subtaskDetails[subtask.id].estimated_hours}
                          />
                        )}
                        <div className="text-right">
                          <div className="font-bold text-gray-900">
                            ₦{parseFloat(subtask.budget_cngn).toLocaleString()}
                          </div>
                          <div className="text-xs text-gray-500">Budget</div>
                        </div>
                        
                        {canClaim && subtask.status === 'open' && (
                          <button
                            onClick={(e) => { e.stopPropagation(); claimMutation.mutate(subtask.id) }}
                            disabled={claimMutation.isPending}
                            className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors"
                          >
                            {claimMutation.isPending ? 'Claiming...' : 'Claim Task'}
                          </button>
                        )}
                        
                        {subtask.claimed_by === user?.id && (subtask.status === 'claimed' || subtask.status === 'in_progress') && (
                          <button 
                            className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white text-sm font-medium rounded-lg transition-colors"
                            onClick={(e) => {
                              e.stopPropagation()
                              setSubmissionModal({
                                isOpen: true,
                                subtaskId: subtask.id,
                                taskTitle: subtask.title,
                              })
                            }}
                          >
                            Submit Work
                          </button>
                        )}

                        {subtask.status === 'submitted' && task.client_id === user?.id && (
                          <button 
                            className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-medium rounded-lg transition-colors"
                            onClick={(e) => {
                              e.stopPropagation()
                              const detail = subtaskDetails[subtask.id]
                              setReviewModal({
                                isOpen: true,
                                subtaskId: subtask.id,
                                taskTitle: subtask.title,
                                submission: detail?.submissions?.[0] ? {
                                  content_summary: detail.submissions[0].content_summary,
                                  artifact_ipfs_hash: detail.submissions[0].artifact_ipfs_hash,
                                  artifact_type: detail.submissions[0].artifact_type,
                                  submitted_at: detail.submissions[0].submitted_at,
                                } : undefined,
                              })
                            }}
                          >
                            Review
                          </button>
                        )}

                        <span className={`text-gray-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </span>
                      </div>
                    </div>
                  </div>

                  {isExpanded && details && (
                    <div className="px-8 pb-6 space-y-6">
                      <div className="ml-12 pl-6 border-l-2 border-gray-200 space-y-6">
                        <p className="text-gray-600 leading-relaxed">{details.description}</p>

                        <div className="flex flex-wrap gap-4">
                          {details.estimated_hours && (
                            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200">
                              <span className="text-lg">⏱️</span>
                              <div>
                                <div className="text-xs text-gray-500">Estimated Time</div>
                                <div className="font-semibold text-gray-900">{details.estimated_hours} hours</div>
                              </div>
                            </div>
                          )}
                          {/* Countdown Timer - shows when subtask is claimed/in_progress */}
                          {(subtask.status === 'claimed' || subtask.status === 'in_progress') && (
                            <CountdownTimer
                              deadline={details.deadline}
                              claimedAt={details.claimed_at}
                              estimatedHours={details.estimated_hours}
                              size="md"
                            />
                          )}
                          {details.tools_required && details.tools_required.length > 0 && (
                            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200">
                              <span className="text-lg">🛠️</span>
                              <div>
                                <div className="text-xs text-gray-500">Tools Required</div>
                                <div className="flex flex-wrap gap-1.5 mt-1">
                                  {details.tools_required.map((tool: string, idx: number) => (
                                    <span key={idx} className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-md font-medium">{tool}</span>
                                  ))}
                                </div>
                              </div>
                            </div>
                          )}
                        </div>

                        {details.acceptance_criteria && details.acceptance_criteria.length > 0 && (
                          <div className="bg-white rounded-xl border border-gray-200 p-5">
                            <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-3">
                              <span>✅</span> Acceptance Criteria
                            </h4>
                            <ul className="space-y-2">
                              {details.acceptance_criteria.map((criterion: string, idx: number) => (
                                <li key={idx} className="flex items-start gap-3 text-sm text-gray-700">
                                  <span className="flex-shrink-0 w-5 h-5 rounded border-2 border-gray-300 bg-white mt-0.5"></span>
                                  <span>{criterion}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {details.deliverables && details.deliverables.length > 0 && (
                          <div>
                            <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-3">
                              <span>📦</span> Deliverables
                            </h4>
                            <div className="grid gap-3">
                              {details.deliverables.map((d: DeliverableItem) => (
                                <div key={d.id} className="flex items-start gap-4 p-4 bg-white rounded-xl border border-gray-200">
                                  <span className="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-lg">
                                    {d.type === 'dataset' ? '📊' : d.type === 'file' ? '📁' : d.type === 'text' ? '📝' : d.type === 'code' ? '💻' : '📎'}
                                  </span>
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <span className="font-medium text-gray-900">{d.title}</span>
                                      <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-md">{d.type}</span>
                                      {d.format_hint && <span className="px-2 py-0.5 bg-blue-50 text-blue-600 text-xs rounded-md">{d.format_hint}</span>}
                                      {d.required && <span className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded-md font-medium">Required</span>}
                                    </div>
                                    <p className="text-sm text-gray-500 mt-1">{d.description}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {details.references && details.references.length > 0 && (
                          <div>
                            <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-3">
                              <span>📚</span> References
                            </h4>
                            <div className="grid gap-2">
                              {details.references.map((ref: ReferenceItem) => (
                                <a
                                  key={ref.id}
                                  href={ref.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="group flex items-center justify-between p-3 bg-white hover:bg-gray-50 rounded-lg border border-gray-200 transition-colors"
                                >
                                  <div className="flex items-center gap-3">
                                    <span className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-sm">
                                      {ref.type === 'paper' ? '📄' : ref.type === 'dataset' ? '📊' : ref.type === 'document' ? '📝' : '🔗'}
                                    </span>
                                    <span className="font-medium text-gray-900 group-hover:text-primary-500 transition-colors">{ref.title}</span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    {ref.required && <span className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded-md font-medium">Required</span>}
                                    <span className="text-gray-400 group-hover:text-primary-500">→</span>
                                  </div>
                                </a>
                              ))}
                            </div>
                          </div>
                        )}

                        {details.example_output && (
                          <div>
                            <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-3">
                              <span>💡</span> Example Output
                            </h4>
                            <pre className="bg-gray-900 text-gray-100 p-4 rounded-xl text-sm overflow-x-auto font-mono">
                              {details.example_output}
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {isExpanded && !details && (
                    <div className="px-8 pb-6">
                      <div className="ml-12 pl-6 border-l-2 border-gray-200">
                        <div className="flex items-center gap-2 text-gray-500">
                          <div className="animate-spin w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full"></div>
                          <span>Loading details...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          <div className="px-8 py-12 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center text-3xl">📋</div>
            <p className="text-gray-500 font-medium">No subtasks yet</p>
            <p className="text-sm text-gray-400 mt-1">Task needs to be decomposed into subtasks</p>
          </div>
        )}
      </div>

      {/* Actions */}
      {!isAuthenticated && (
        <div className="card p-6 text-center bg-gray-50">
          <p className="text-gray-600">Connect your wallet to claim subtasks and earn rewards.</p>
        </div>
      )}

      <SubmissionModal
        isOpen={submissionModal.isOpen}
        onClose={() => setSubmissionModal({ isOpen: false, subtaskId: '', taskTitle: '' })}
        subtaskId={submissionModal.subtaskId}
        taskTitle={submissionModal.taskTitle}
        taskId={taskId!}
      />

      <ReviewModal
        isOpen={reviewModal.isOpen}
        onClose={() => setReviewModal({ isOpen: false, subtaskId: '', taskTitle: '' })}
        subtaskId={reviewModal.subtaskId}
        taskTitle={reviewModal.taskTitle}
        taskId={taskId!}
        submission={reviewModal.submission}
      />

      <DecomposeTaskModal
        isOpen={showDecomposeModal}
        onClose={() => setShowDecomposeModal(false)}
        taskId={taskId!}
        taskTitle={task.title}
        researchQuestion={task.research_question}
        onSuccess={() => queryClient.invalidateQueries({ queryKey: ['task', taskId] })}
      />
    </div>
  )
}
