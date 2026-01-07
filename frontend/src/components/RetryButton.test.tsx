import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import RetryButton from './RetryButton'

describe('RetryButton', () => {
  it('renders with default text', () => {
    render(<RetryButton onClick={() => {}} />)

    expect(screen.getByText('Retry')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<RetryButton onClick={handleClick} />)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('shows loading state', () => {
    render(<RetryButton onClick={() => {}} isLoading={true} />)

    expect(screen.getByText('Retrying...')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('is not disabled when not loading', () => {
    render(<RetryButton onClick={() => {}} isLoading={false} />)

    expect(screen.getByRole('button')).not.toBeDisabled()
  })

  it('applies custom className', () => {
    render(<RetryButton onClick={() => {}} className="custom-class" />)

    expect(screen.getByRole('button')).toHaveClass('custom-class')
  })

  it('has spinner animation when loading', () => {
    const { container } = render(<RetryButton onClick={() => {}} isLoading={true} />)

    const svg = container.querySelector('svg')
    expect(svg).toHaveClass('animate-spin')
  })
})
