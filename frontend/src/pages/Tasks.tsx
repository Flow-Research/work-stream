import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { taskService } from '../services/api'
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
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [page, setPage] = useState(1)

  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks', statusFilter, page],
    queryFn: () => taskService.list({ status: statusFilter || undefined, page, limit: 20 }),
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
        <h1 className="text-2xl font-bold text-gray-900">Research Tasks</h1>
        
        {/* Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input w-48"
        >
          <option value="">All Status</option>
          <option value="funded">Funded</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Task List */}
      {tasks.length === 0 ? (
        <div className="card p-8 text-center">
          <p className="text-gray-500">No tasks found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <Link
              key={task.id}
              to={`/tasks/${task.id}`}
              className="card p-6 block hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h2 className="text-lg font-semibold text-gray-900">{task.title}</h2>
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
    </div>
  )
}
