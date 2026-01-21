import axios, { AxiosError } from 'axios'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('flow-auth')
  if (token) {
    try {
      const parsed = JSON.parse(token)
      if (parsed.state?.token) {
        config.headers.Authorization = `Bearer ${parsed.state.token}`
      }
    } catch {
      // Invalid token format
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.code === 'ERR_NETWORK') {
      toast.error('Network error. Please check your connection.')
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timed out. Please try again.')
    } else if (error.response) {
      const status = error.response.status
      
      if (status === 401) {
        localStorage.removeItem('flow-auth')
        toast.error('Session expired. Please reconnect your wallet.')
      } else if (status === 403) {
        toast.error('You do not have permission to perform this action.')
      } else if (status >= 500) {
        toast.error('Server error. Please try again later.')
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth service
export const authService = {
  async getNonce(walletAddress: string) {
    const response = await api.post('/auth/nonce', { wallet_address: walletAddress })
    return response.data
  },

  async verify(walletAddress: string, signature: string, nonce: string) {
    const response = await api.post('/auth/verify', {
      wallet_address: walletAddress,
      signature,
      nonce,
    })
    return response.data
  },

  async getProfile(token: string) {
    const response = await api.get('/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return response.data
  },
}

// Task service
export const taskService = {
  async list(params?: { status?: string; skills?: string; search?: string; page?: number; limit?: number; include_drafts?: boolean }) {
    const response = await api.get('/tasks', { params })
    return response.data
  },

  async get(taskId: string) {
    const response = await api.get(`/tasks/${taskId}`)
    return response.data
  },

  async create(data: {
    title: string
    description: string
    research_question: string
    total_budget_cngn: string
    skills_required?: string[]
    deadline?: string
    background_context?: string
    methodology_notes?: string
  }) {
    const response = await api.post('/tasks', data)
    return response.data
  },

  async fund(taskId: string, escrowTxHash: string) {
    const response = await api.post(`/tasks/${taskId}/fund`, { escrow_tx_hash: escrowTxHash })
    return response.data
  },

  async decompose(taskId: string) {
    const response = await api.post(`/tasks/${taskId}/decompose`)
    return response.data
  },
}

// Subtask service
export const subtaskService = {
  async list(params?: { status?: string; task_id?: string; page?: number; limit?: number }) {
    const response = await api.get('/subtasks', { params })
    return response.data
  },

  async get(subtaskId: string) {
    const response = await api.get(`/subtasks/${subtaskId}`)
    return response.data
  },

  async claim(subtaskId: string, collaborators?: string[], splits?: number[]) {
    const response = await api.post(`/subtasks/${subtaskId}/claim`, { collaborators, splits })
    return response.data
  },

  async unclaim(subtaskId: string) {
    const response = await api.post(`/subtasks/${subtaskId}/unclaim`)
    return response.data
  },

  async submit(subtaskId: string, contentSummary: string, artifact?: File) {
    const formData = new FormData()
    formData.append('content_summary', contentSummary)
    if (artifact) {
      formData.append('artifact', artifact)
    }
    const response = await api.post(`/subtasks/${subtaskId}/submit`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async approve(subtaskId: string, reviewNotes?: string) {
    const response = await api.post(`/subtasks/${subtaskId}/approve`, { review_notes: reviewNotes })
    return response.data
  },

  async reject(subtaskId: string, reviewNotes: string) {
    const response = await api.post(`/subtasks/${subtaskId}/reject`, { review_notes: reviewNotes })
    return response.data
  },
}

// AI service
export const aiService = {
  async decomposeTask(researchQuestion: string, budget: number, context?: string) {
    const response = await api.post('/ai/decompose-task', {
      research_question: researchQuestion,
      budget,
      context,
    })
    return response.data
  },

  async discoverPapers(query: string, limit?: number) {
    const response = await api.post('/ai/discover-papers', { query, limit })
    return response.data
  },
}

// Skills service
export const skillsService = {
  async list(params?: { category_id?: string; search?: string; include_inactive?: boolean }) {
    const response = await api.get('/skills', { params })
    return response.data
  },

  async listGrouped(params?: { include_inactive?: boolean }) {
    const response = await api.get('/skills/grouped', { params })
    return response.data
  },

  async get(skillId: string) {
    const response = await api.get(`/skills/${skillId}`)
    return response.data
  },

  async create(data: { name: string; description?: string; category_id?: string; display_order?: number }) {
    const response = await api.post('/skills', data)
    return response.data
  },

  async update(skillId: string, data: { name?: string; description?: string; category_id?: string; is_active?: boolean; display_order?: number }) {
    const response = await api.patch(`/skills/${skillId}`, data)
    return response.data
  },

  async delete(skillId: string) {
    await api.delete(`/skills/${skillId}`)
  },

  // Categories
  async listCategories(params?: { include_inactive?: boolean }) {
    const response = await api.get('/skills/categories/', { params })
    return response.data
  },

  async createCategory(data: { name: string; description?: string; color?: string; icon?: string; display_order?: number }) {
    const response = await api.post('/skills/categories/', data)
    return response.data
  },

  async updateCategory(categoryId: string, data: { name?: string; description?: string; color?: string; icon?: string; is_active?: boolean; display_order?: number }) {
    const response = await api.patch(`/skills/categories/${categoryId}`, data)
    return response.data
  },

  async deleteCategory(categoryId: string) {
    await api.delete(`/skills/categories/${categoryId}`)
  },
}

// Admin service
export const adminService = {
  async listUsers(params?: { verified?: boolean; banned?: boolean; page?: number; limit?: number }) {
    const response = await api.get('/admin/users', { params })
    return response.data
  },

  async verifyUser(userId: string) {
    const response = await api.post(`/admin/users/${userId}/verify`)
    return response.data
  },

  async banUser(userId: string, reason: string) {
    const response = await api.post(`/admin/users/${userId}/ban`, { reason })
    return response.data
  },

  async listDisputes(params?: { status?: string; page?: number; limit?: number }) {
    const response = await api.get('/admin/disputes', { params })
    return response.data
  },

  async resolveDispute(disputeId: string, winnerId: string, resolution: string) {
    const response = await api.post(`/admin/disputes/${disputeId}/resolve`, {
      winner_id: winnerId,
      resolution,
    })
    return response.data
  },
}

export default api
