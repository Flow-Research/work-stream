import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ReviewModal from './ReviewModal'

vi.mock('../services/api', () => ({
  subtaskService: {
    reviewSubmission: vi.fn().mockResolvedValue({}),
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
  taskTitle: 'Test Task Title',
}

describe('ReviewModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders nothing when isOpen is false', () => {
    renderWithProviders(<ReviewModal {...defaultProps} isOpen={false} />)
    expect(screen.queryByText('Review Work')).not.toBeInTheDocument()
  })

  it('renders modal content when isOpen is true', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    expect(screen.getByText('Review Work')).toBeInTheDocument()
  })

  it('has quality rating buttons', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('has a text area for review notes', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/detailed feedback/i)
    expect(textarea).toBeInTheDocument()
  })

  it('allows typing review notes', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/detailed feedback/i)

    fireEvent.change(textarea, { target: { value: 'Great work!' } })
    expect(textarea).toHaveValue('Great work!')
  })

  it('closes when close button is clicked', () => {
    const onClose = vi.fn()
    renderWithProviders(<ReviewModal {...defaultProps} onClose={onClose} />)

    const closeButton = screen.getByRole('button', { name: '' })
    fireEvent.click(closeButton)
    expect(onClose).toHaveBeenCalled()
  })

  it('has cancel and submit review buttons', () => {
    renderWithProviders(<ReviewModal {...defaultProps} />)
    expect(screen.getByText('Cancel')).toBeInTheDocument()
    expect(screen.getByText('Submit Review')).toBeInTheDocument()
  })
})
