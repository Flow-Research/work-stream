import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ReviewModal from './ReviewModal'

vi.mock('../services/api', () => ({
  subtaskService: {
    approve: vi.fn().mockResolvedValue({}),
    reject: vi.fn().mockResolvedValue({}),
  },
}))

vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

const defaultProps = {
  isOpen: true,
  onClose: vi.fn(),
  subtaskId: 'subtask-123',
  subtaskTitle: 'Test Subtask',
  taskId: 'task-123',
  submission: {
    content_summary: 'This is my work summary',
    artifact_ipfs_hash: 'QmTestHash123',
    artifact_type: 'json',
    submitted_at: '2025-01-08T10:00:00Z',
  },
}

describe('ReviewModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders nothing when isOpen is false', () => {
    renderWithProviders(<ReviewModal {...defaultProps} isOpen={false} />)
    expect(screen.queryByText('Review Submission')).not.toBeInTheDocument()
  })

  it('renders modal content when isOpen is true', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    expect(screen.getByText('Review Submission')).toBeInTheDocument()
    expect(screen.getByText('Test Subtask')).toBeInTheDocument()
  })

  it('displays submission details', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    expect(screen.getByText('This is my work summary')).toBeInTheDocument()
    expect(screen.getByText(/View JSON file/i)).toBeInTheDocument()
  })

  it('has approve and reject buttons', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    expect(screen.getByText('Approve')).toBeInTheDocument()
    expect(screen.getByText('Reject')).toBeInTheDocument()
  })

  it('has a text area for review notes', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/Optional feedback/i)
    expect(textarea).toBeInTheDocument()
  })

  it('closes when close button is clicked', () => {
    const onClose = vi.fn()
    renderWithProviders(<ReviewModal {...defaultProps} onClose={onClose} />)
    
    const closeButton = screen.getByRole('button', { name: '' })
    fireEvent.click(closeButton)
    expect(onClose).toHaveBeenCalled()
  })

  it('allows typing review notes', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/Optional feedback/i)
    
    fireEvent.change(textarea, { target: { value: 'Great work!' } })
    expect(textarea).toHaveValue('Great work!')
  })

  it('shows artifact link with correct IPFS URL', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    const link = screen.getByText(/View JSON file/i).closest('a')
    expect(link).toHaveAttribute(
      'href',
      'https://gateway.pinata.cloud/ipfs/QmTestHash123'
    )
    expect(link).toHaveAttribute('target', '_blank')
  })

  it('displays submitted date', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    expect(screen.getByText('Submitted')).toBeInTheDocument()
  })
})
