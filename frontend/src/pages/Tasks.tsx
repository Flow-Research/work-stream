import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { taskService } from '../services/api'
import { useAuthStore } from '../stores/auth'
import CreateTaskModal from '../components/CreateTaskModal'
import type { Task, TaskStatus } from '../types'

const statusColors: Record<TaskStatus, string> = {
  draft: 'badge-gray',
  funded: 'badge-info',
  decomposed: 'badge-info',
  in_progress: 'badge-warning',
  in_review: 'badge-warning',
  completed: 'badge-success',
  cancelled: 'badge-error',
  disputed: 'badge-error',
}

const statusLabels: Record<TaskStatus, string> = {
  draft: 'Draft',
  funded: 'Funded',
  decomposed: 'Decomposed',
  in_progress: 'In Progress',
  in_review: 'In Review',
  completed: 'Completed',
  cancelled: 'Cancelled',
  disputed: 'Disputed',
}

export default function Tasks() {
  const { user } = useAuthStore()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [debouncedSearch, setDebouncedSearch] = useState<string>('')
  const [page, setPage] = useState(1)
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery)
      if (searchQuery !== debouncedSearch) {
        setPage(1) // Reset to first page when search changes
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks', statusFilter, debouncedSearch, page, user?.is_admin],
    queryFn: () => taskService.list({
      status: statusFilter || undefined,
      search: debouncedSearch || undefined,
      page,
      limit: 20,
      include_drafts: user?.is_admin || false,
    }),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-red-600">
        Error loading tasks. Please try again.
      </div>
    )
  }

  const tasks: Task[] = data?.tasks || []
  const total = data?.total || 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary-800 tracking-tight">Tasks</h1>

        <div className="flex items-center gap-4">
          {/* Search Input */}
          <div className="relative">
            <svg
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tasks..."
              className="input pl-10 w-64"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input w-48"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="funded">Funded</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>

          {user?.is_admin && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-all duration-200 flex items-center gap-2 shadow-sm hover:shadow-md"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Task
            </button>
          )}
        </div>
      </div>

      {/* Task List */}
      {tasks.length === 0 ? (
        <div className="card p-8 text-center">
          {debouncedSearch ? (
            <>
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center text-3xl">🔍</div>
              <p className="text-gray-600 font-medium">No tasks found for "{debouncedSearch}"</p>
              <p className="text-sm text-gray-400 mt-1">Try adjusting your search terms</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                Clear search
              </button>
            </>
          ) : (
            <p className="text-gray-500">No tasks found</p>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <Link
              key={task.id}
              to={`/tasks/${task.id}`}
              className="card p-6 block hover:shadow-md hover:border-primary-200 transition-all duration-200 group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h2 className="text-lg font-semibold text-primary-700 group-hover:text-primary-600 transition-colors">{task.title}</h2>
                    <span className={statusColors[task.status]}>
                      {statusLabels[task.status]}
                    </span>
                  </div>
                  <p className="mt-2 text-gray-600 line-clamp-2">{task.description}</p>

                  {/* Skills */}
                  {task.skills_required && task.skills_required.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {task.skills_required.map((skill) => (
                        <span key={skill} className="badge-gray">
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Budget */}
                <div className="text-right ml-4">
                  <div className="text-lg font-semibold text-primary-600">
                    {parseFloat(task.total_budget_cngn).toLocaleString()} cNGN
                  </div>
                  <div className="text-sm text-gray-500">
                    {task.subtasks?.length || 0} subtasks
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 20 && (
        <div className="flex items-center justify-between">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-secondary"
          >
            Previous
          </button>
          <span className="text-gray-600">
            Page {page} of {Math.ceil(total / 20)}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 20 >= total}
            className="btn-secondary"
          >
            Next
          </button>
        </div>
      )}

      <CreateTaskModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  )
}
