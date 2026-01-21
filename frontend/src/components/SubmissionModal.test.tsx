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
  taskTitle: 'Test Task',
}

describe('SubmissionModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders nothing when isOpen is false', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} isOpen={false} />)
    expect(screen.queryByText('Submit Work')).not.toBeInTheDocument()
  })

  it('renders modal content when isOpen is true', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    expect(screen.getByRole('heading', { name: 'Submit Work' })).toBeInTheDocument()
    expect(screen.getByText('Test Task')).toBeInTheDocument()
  })

  it('has a text area for work summary', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/Describe what you accomplished/i)
    expect(textarea).toBeInTheDocument()
  })

  it('allows typing work summary', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/Describe what you accomplished/i)

    fireEvent.change(textarea, { target: { value: 'I completed the work!' } })
    expect(textarea).toHaveValue('I completed the work!')
  })

  it('has artifact section with add button', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    expect(screen.getByText('Artifacts')).toBeInTheDocument()
    expect(screen.getByText('+ Add Artifact')).toBeInTheDocument()
  })

  it('closes when close button is clicked', () => {
    const onClose = vi.fn()
    renderWithProviders(<SubmissionModal {...defaultProps} onClose={onClose} />)

    const closeButton = screen.getByRole('button', { name: '' })
    fireEvent.click(closeButton)
    expect(onClose).toHaveBeenCalled()
  })

  it('has cancel and submit buttons', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    expect(screen.getByText('Cancel')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Submit Work' })).toBeInTheDocument()
  })

  it('allows adding artifacts', () => {
    renderWithProviders(<SubmissionModal {...defaultProps} />)
    const titleInput = screen.getByPlaceholderText('Artifact title')
    const addButton = screen.getByText('+ Add Artifact')

    fireEvent.change(titleInput, { target: { value: 'Test Dataset' } })
    fireEvent.click(addButton)

    expect(screen.getByText('Test Dataset')).toBeInTheDocument()
  })
})
