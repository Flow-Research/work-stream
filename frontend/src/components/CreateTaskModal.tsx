import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { taskService } from '../services/api'
import { useDummyData, dummyDataTemplates } from '../hooks/useDummyData'
import SkillsSelector from './SkillsSelector'

interface CreateTaskModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

function CreateTaskModal({ isOpen, onClose, onSuccess }: CreateTaskModalProps) {
  const queryClient = useQueryClient()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [researchQuestion, setResearchQuestion] = useState('')
  const [budget, setBudget] = useState('')
  const [skills, setSkills] = useState<string[]>([])
  const [deadline, setDeadline] = useState('')
  const [backgroundContext, setBackgroundContext] = useState('')
  const [methodologyNotes, setMethodologyNotes] = useState('')

  // Use dummy data with keyboard shortcut
  useDummyData(
    'taskCreation',
    dummyDataTemplates.taskCreation,
    (data) => {
      setTitle(data.title)
      setDescription(data.description)
      setResearchQuestion(data.research_question)
      setBudget(data.budget)
      setSkills(data.skills)
      setDeadline(data.deadline)
      setBackgroundContext(data.background_context)
      setMethodologyNotes(data.methodology_notes)
    },
    isOpen
  )

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setTitle('')
      setDescription('')
      setResearchQuestion('')
      setBudget('')
      setSkills([])
      setDeadline('')
      setBackgroundContext('')
      setMethodologyNotes('')
    }
  }, [isOpen])

  const createMutation = useMutation({
    mutationFn: () => taskService.create({
      title,
      description,
      research_question: researchQuestion,
      total_budget_cngn: budget,
      skills_required: skills.length > 0 ? skills : undefined,
      deadline: deadline || undefined,
      background_context: backgroundContext || undefined,
      methodology_notes: methodologyNotes || undefined,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task created successfully!')
      handleClose()
      onSuccess?.()
    },
    onError: () => {
      toast.error('Failed to create task. Please try again.')
    },
  })

  const handleClose = () => {
    setTitle('')
    setDescription('')
    setResearchQuestion('')
    setBudget('')
    setSkills([])
    setDeadline('')
    setBackgroundContext('')
    setMethodologyNotes('')
    onClose()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !description.trim() || !researchQuestion.trim() || !budget) {
      toast.error('Please fill in all required fields')
      return
    }
    createMutation.mutate()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={handleClose} />
        
        <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl transform transition-all max-h-[90vh] overflow-y-auto">
          <div className="px-6 py-4 border-b border-gray-200 sticky top-0 bg-white z-10">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Create New Task</h2>
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
                Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Systematic Review of AI in Healthcare"
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Research Question <span className="text-red-500">*</span>
              </label>
              <textarea
                value={researchQuestion}
                onChange={(e) => setResearchQuestion(e.target.value)}
                placeholder="What specific question should this research answer?"
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-shadow"
                rows={3}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description <span className="text-red-500">*</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Provide a detailed description of research task..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-shadow"
                rows={5}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Budget (cNGN) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  placeholder="50000"
                  min="0"
                  step="1000"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Deadline</label>
                <input
                  type="date"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Skills Required</label>
              <SkillsSelector
                selectedSlugs={skills}
                onChange={setSkills}
                maxSelections={10}
                placeholder="Select required skills..."
              />
              <p className="mt-1 text-xs text-gray-500">Select up to 10 skills that are required for this task</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Background Context</label>
              <textarea
                value={backgroundContext}
                onChange={(e) => setBackgroundContext(e.target.value)}
                placeholder="Any relevant background information or context..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-shadow"
                rows={5}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Methodology Notes</label>
              <textarea
                value={methodologyNotes}
                onChange={(e) => setMethodologyNotes(e.target.value)}
                placeholder="Preferred research methodology or approach..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-shadow"
                rows={5}
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
                disabled={createMutation.isPending}
                className="flex-1 px-4 py-2.5 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {createMutation.isPending ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Creating...
                  </>
                ) : (
                  'Create Task'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default CreateTaskModal
