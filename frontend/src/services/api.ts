import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('flow-auth')
  if (token) {
    try {
      const parsed = JSON.parse(token)
      if (parsed.state?.token) {
        config.headers.Authorization = `Bearer ${parsed.state.token}`
      }
    } catch (e) {
      // Invalid token format
    }
  }
  return config
})

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
  async list(params?: { status?: string; skills?: string; page?: number; limit?: number }) {
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
