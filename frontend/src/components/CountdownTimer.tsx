import { useCountdown, calculateDeadlineFromEstimate } from '../hooks/useCountdown'

interface CountdownTimerProps {
  /** Explicit deadline date */
  deadline?: string | null
  /** When the task was claimed (for calculating implicit deadline) */
  claimedAt?: string | null
  /** Estimated hours to complete (for calculating implicit deadline) */
  estimatedHours?: string | number | null
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
  /** Show full countdown or compact version */
  compact?: boolean
  /** Additional CSS classes */
  className?: string
}

export default function CountdownTimer({
  deadline,
  claimedAt,
  estimatedHours,
  size = 'md',
  compact = false,
  className = '',
}: CountdownTimerProps) {
  // Determine the effective deadline
  const effectiveDeadline = deadline
    ? new Date(deadline)
    : calculateDeadlineFromEstimate(claimedAt, estimatedHours)

  const countdown = useCountdown(effectiveDeadline)

  if (!countdown) return null

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  }

  // Color based on urgency
  const getColorClasses = () => {
    if (countdown.isExpired) {
      return 'bg-red-100 text-red-700 border-red-200'
    }
    if (countdown.isCritical) {
      return 'bg-red-50 text-red-600 border-red-200 animate-pulse'
    }
    if (countdown.isUrgent) {
      return 'bg-amber-50 text-amber-700 border-amber-200'
    }
    return 'bg-emerald-50 text-emerald-700 border-emerald-200'
  }

  const getIconColor = () => {
    if (countdown.isExpired || countdown.isCritical) {
      return 'text-red-500'
    }
    if (countdown.isUrgent) {
      return 'text-amber-500'
    }
    return 'text-emerald-500'
  }

  if (compact) {
    return (
      <div className={`inline-flex items-center gap-1.5 ${sizeClasses[size]} ${className}`}>
        <svg
          className={`${iconSizes[size]} ${getIconColor()}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span className={countdown.isExpired ? 'text-red-600 font-medium' : countdown.isCritical ? 'text-red-600' : countdown.isUrgent ? 'text-amber-600' : 'text-gray-600'}>
          {countdown.shortFormatted}
        </span>
      </div>
    )
  }

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${getColorClasses()} ${sizeClasses[size]} ${className}`}>
      <svg
        className={`${iconSizes[size]} flex-shrink-0`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <div className="flex flex-col">
        <span className="font-medium">
          {countdown.isExpired ? 'Deadline passed' : 'Time remaining'}
        </span>
        {!countdown.isExpired && (
          <span className="font-bold tabular-nums">
            {countdown.formatted}
          </span>
        )}
      </div>
    </div>
  )
}

/** Inline countdown for use in lists/tables */
export function InlineCountdown({
  deadline,
  claimedAt,
  estimatedHours,
  className = '',
}: Omit<CountdownTimerProps, 'size' | 'compact'>) {
  const effectiveDeadline = deadline
    ? new Date(deadline)
    : calculateDeadlineFromEstimate(claimedAt, estimatedHours)

  const countdown = useCountdown(effectiveDeadline)

  if (!countdown) return null

  const getColor = () => {
    if (countdown.isExpired) return 'text-red-600'
    if (countdown.isCritical) return 'text-red-500'
    if (countdown.isUrgent) return 'text-amber-600'
    return 'text-gray-600'
  }

  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium tabular-nums ${getColor()} ${className}`}>
      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      {countdown.shortFormatted}
    </span>
  )
}
