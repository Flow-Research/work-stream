import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import Tasks from './Tasks'

// Mock the API service
vi.mock('../services/api', () => ({
  taskService: {
    list: vi.fn().mockResolvedValue({
      tasks: [
        {
          id: 'task-1',
          title: 'Test Task',
          description: 'A test task description',
          status: 'draft',
          total_budget_cngn: '1000',
          skills_required: ['research'],
          subtasks: [],
        },
      ],
      total: 1,
      page: 1,
      limit: 20,
    }),
  },
}))

// Mock the auth store
vi.mock('../stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    user: { id: 'user-1', is_admin: true },
  })),
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
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>
  )
}

describe('Tasks Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset URL before each test
    window.history.replaceState({}, '', '/')
  })

  afterEach(() => {
    // Clean up URL after each test
    window.history.replaceState({}, '', '/')
  })

  describe('Status Labels', () => {
    it('displays "Pending" for draft tasks instead of "Draft"', async () => {
      renderWithProviders(<Tasks />)

      // Wait for the task to load
      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      // Check that "Pending" badge is displayed on the task card (not "Draft")
      // The badge has class "badge-gray" and contains "Pending"
      const pendingBadges = screen.getAllByText('Pending')
      // Should have at least one Pending badge (on the task card)
      expect(pendingBadges.length).toBeGreaterThanOrEqual(1)

      // Find the badge specifically (in a span with badge-gray class)
      const taskBadge = pendingBadges.find(
        (el) => el.tagName === 'SPAN' && el.classList.contains('badge-gray')
      )
      expect(taskBadge).toBeTruthy()

      // Ensure "Draft" text does NOT appear anywhere as a badge label
      const draftElements = screen.queryAllByText('Draft')
      // Filter to only badge elements (not other uses)
      const draftBadges = draftElements.filter(
        (el) => el.tagName === 'SPAN' && el.classList.contains('badge-gray')
      )
      expect(draftBadges).toHaveLength(0)
    })
  })

  describe('Status Filter Dropdown', () => {
    it('renders a status filter dropdown', async () => {
      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      const dropdown = screen.getByRole('combobox')
      expect(dropdown).toBeInTheDocument()
    })

    it('has "All Status" as the default selected option', async () => {
      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      const dropdown = screen.getByRole('combobox') as HTMLSelectElement
      expect(dropdown.value).toBe('')
    })

    it('contains all 8 status options plus "All Status"', async () => {
      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      const dropdown = screen.getByRole('combobox')
      const options = dropdown.querySelectorAll('option')

      expect(options).toHaveLength(9) // All Status + 8 statuses

      // Verify all options are present with correct labels
      const optionTexts = Array.from(options).map((opt) => opt.textContent)
      expect(optionTexts).toContain('All Status')
      expect(optionTexts).toContain('Pending') // Not "Draft"
      expect(optionTexts).toContain('Funded')
      expect(optionTexts).toContain('Decomposed')
      expect(optionTexts).toContain('In Progress')
      expect(optionTexts).toContain('In Review')
      expect(optionTexts).toContain('Completed')
      expect(optionTexts).toContain('Cancelled')
      expect(optionTexts).toContain('Disputed')
    })

    it('shows "Pending" in dropdown but uses "draft" as the value', async () => {
      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      const dropdown = screen.getByRole('combobox')
      const pendingOption = dropdown.querySelector(
        'option[value="draft"]'
      ) as HTMLOptionElement

      expect(pendingOption).toBeInTheDocument()
      expect(pendingOption.textContent).toBe('Pending')
    })

    it('updates filter when a status is selected', async () => {
      const { taskService } = await import('../services/api')
      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      const dropdown = screen.getByRole('combobox')
      fireEvent.change(dropdown, { target: { value: 'draft' } })

      await waitFor(() => {
        expect(taskService.list).toHaveBeenCalledWith(
          expect.objectContaining({ status: 'draft' })
        )
      })
    })
  })

  describe('URL Synchronization', () => {
    it('updates URL when status filter changes', async () => {
      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      const dropdown = screen.getByRole('combobox')
      fireEvent.change(dropdown, { target: { value: 'draft' } })

      // Check URL was updated
      expect(window.location.search).toContain('status=draft')
    })

    it('removes status from URL when "All Status" is selected', async () => {
      // Start with a status in the URL
      window.history.replaceState({}, '', '/?status=draft')

      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      const dropdown = screen.getByRole('combobox')

      // Select "All Status" (empty value)
      fireEvent.change(dropdown, { target: { value: '' } })

      // Check URL no longer has status param
      expect(window.location.search).not.toContain('status=')
    })

    it('initializes filter from URL params on load', async () => {
      // Set URL with status param before rendering
      window.history.replaceState({}, '', '/?status=funded')

      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      const dropdown = screen.getByRole('combobox') as HTMLSelectElement
      expect(dropdown.value).toBe('funded')
    })
  })

  describe('Search and Filter Combination', () => {
    it('renders search input alongside filter', async () => {
      renderWithProviders(<Tasks />)

      await waitFor(() => {
        expect(screen.getByText('Test Task')).toBeInTheDocument()
      })

      // Verify both search and filter are present together
      const searchInput = screen.getByPlaceholderText('Search tasks...')
      const filterDropdown = screen.getByRole('combobox')

      expect(searchInput).toBeInTheDocument()
      expect(filterDropdown).toBeInTheDocument()
    })
  })
})
