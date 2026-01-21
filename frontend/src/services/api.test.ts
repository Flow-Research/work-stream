import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { authService, taskService, subtaskService } from './api'

vi.mock('axios', () => {
  const mockAxios: Record<string, unknown> = {
    create: vi.fn(() => mockAxios),
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  }
  return { default: mockAxios }
})

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('TC-FE-001: getNonce calls correct endpoint with wallet address', async () => {
    const mockResponse = { data: { nonce: 'abc123' } }
    vi.mocked(axios.post).mockResolvedValue(mockResponse)

    const result = await authService.getNonce('0x1234567890abcdef')

    expect(axios.post).toHaveBeenCalledWith('/auth/nonce', {
      wallet_address: '0x1234567890abcdef',
    })
    expect(result).toEqual({ nonce: 'abc123' })
  })

  it('TC-FE-002: verify sends signature and nonce correctly', async () => {
    const mockResponse = { data: { token: 'jwt-token' } }
    vi.mocked(axios.post).mockResolvedValue(mockResponse)

    const result = await authService.verify('0xaddr', 'sig123', 'nonce456')

    expect(axios.post).toHaveBeenCalledWith('/auth/verify', {
      wallet_address: '0xaddr',
      signature: 'sig123',
      nonce: 'nonce456',
    })
    expect(result).toEqual({ token: 'jwt-token' })
  })
})

describe('taskService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('list returns paginated tasks', async () => {
    const mockTasks = { data: { tasks: [], total: 0 } }
    vi.mocked(axios.get).mockResolvedValue(mockTasks)

    const result = await taskService.list({ status: 'open', page: 1 })

    expect(axios.get).toHaveBeenCalledWith('/tasks', {
      params: { status: 'open', page: 1 },
    })
    expect(result).toEqual({ tasks: [], total: 0 })
  })

  it('get returns task by ID', async () => {
    const mockTask = { data: { id: '123', title: 'Test' } }
    vi.mocked(axios.get).mockResolvedValue(mockTask)

    const result = await taskService.get('123')

    expect(axios.get).toHaveBeenCalledWith('/tasks/123')
    expect(result).toEqual({ id: '123', title: 'Test' })
  })
})

describe('subtaskService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('TC-FE-005: submit sends FormData with content and optional file', async () => {
    const mockResponse = { data: { id: 'sub-123', status: 'pending' } }
    vi.mocked(axios.post).mockResolvedValue(mockResponse)

    const file = new File(['test'], 'test.json', { type: 'application/json' })
    const result = await subtaskService.submit('sub-123', 'My summary', file)

    expect(axios.post).toHaveBeenCalled()
    const [url, formData, config] = vi.mocked(axios.post).mock.calls[0]
    expect(url).toBe('/subtasks/sub-123/submit')
    expect(formData).toBeInstanceOf(FormData)
    expect(config?.headers?.['Content-Type']).toBe('multipart/form-data')
    expect(result).toEqual({ id: 'sub-123', status: 'pending' })
  })

  it('claim calls correct endpoint', async () => {
    const mockResponse = { data: { id: 'sub-123', status: 'claimed' } }
    vi.mocked(axios.post).mockResolvedValue(mockResponse)

    const result = await subtaskService.claim('sub-123')

    expect(axios.post).toHaveBeenCalledWith('/subtasks/sub-123/claim', {
      collaborators: undefined,
      splits: undefined,
    })
    expect(result).toEqual({ id: 'sub-123', status: 'claimed' })
  })

  it('approve calls correct endpoint with optional notes', async () => {
    const mockResponse = { data: { id: 'sub-123', status: 'approved' } }
    vi.mocked(axios.post).mockResolvedValue(mockResponse)

    const result = await subtaskService.approve('sub-123', 'Great work!')

    expect(axios.post).toHaveBeenCalledWith('/subtasks/sub-123/approve', {
      review_notes: 'Great work!',
    })
    expect(result).toEqual({ id: 'sub-123', status: 'approved' })
  })

  it('reject calls correct endpoint with required notes', async () => {
    const mockResponse = { data: { id: 'sub-123', status: 'rejected' } }
    vi.mocked(axios.post).mockResolvedValue(mockResponse)

    const result = await subtaskService.reject('sub-123', 'Needs more detail')

    expect(axios.post).toHaveBeenCalledWith('/subtasks/sub-123/reject', {
      review_notes: 'Needs more detail',
    })
    expect(result).toEqual({ id: 'sub-123', status: 'rejected' })
  })
})
