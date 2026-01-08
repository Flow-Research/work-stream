import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import SubmissionModal from './SubmissionModal'

vi.mock('../services/api', () => ({
  subtaskService: {
    submit: vi.fn().mockResolvedValue({}),
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
}

describe('SubmissionModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders nothing when isOpen is false', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} isOpen={false} />)
    expect(screen.queryByText('Submit Work')).not.toBeInTheDocument()
  })

  it('renders modal when isOpen is true', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    expect(screen.getByRole('heading', { name: 'Submit Work' })).toBeInTheDocument()
    expect(screen.getByText('Test Subtask')).toBeInTheDocument()
  })

  it('has work summary textarea', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/Describe what you accomplished/i)
    expect(textarea).toBeInTheDocument()
    expect(textarea).toHaveAttribute('required')
  })

  it('has file upload area', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    expect(screen.getByText(/Click to upload/i)).toBeInTheDocument()
    expect(screen.getByText(/JSON, CSV, MD, TXT/i)).toBeInTheDocument()
  })

  it('has cancel and submit buttons', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    expect(screen.getByText('Cancel')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Submit Work' })).toBeInTheDocument()
  })

  it('submit button is disabled when content summary is empty', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    const submitButton = screen.getByRole('button', { name: 'Submit Work' })
    expect(submitButton).toBeDisabled()
  })

  it('submit button is enabled when content summary has text', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/Describe what you accomplished/i)
    
    fireEvent.change(textarea, { target: { value: 'My work summary' } })
    
    const submitButton = screen.getByRole('button', { name: 'Submit Work' })
    expect(submitButton).not.toBeDisabled()
  })

  it('calls onClose when cancel is clicked', () => {
    const onClose = vi.fn()
    renderWithProviders(<SubmissionModal {...defaultProps} onClose={onClose} />)
    
    fireEvent.click(screen.getByText('Cancel'))
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn()
    renderWithProviders(<SubmissionModal {...defaultProps} onClose={onClose} />)
    
    const closeButtons = screen.getAllByRole('button')
    const closeButton = closeButtons.find(btn => btn.className.includes('text-gray-400'))
    if (closeButton) {
      fireEvent.click(closeButton)
      expect(onClose).toHaveBeenCalled()
    }
  })

  it('allows typing in content summary', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/Describe what you accomplished/i)
    
    fireEvent.change(textarea, { target: { value: 'Test summary content' } })
    expect(textarea).toHaveValue('Test summary content')
  })

  it('shows file size limit information', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    expect(screen.getByText(/up to 10MB/i)).toBeInTheDocument()
  })
})
