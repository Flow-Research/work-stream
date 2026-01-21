import { useState, useEffect, useMemo } from 'react'

interface CountdownResult {
  days: number
  hours: number
  minutes: number
  seconds: number
  totalSeconds: number
  isExpired: boolean
  isUrgent: boolean // less than 24 hours remaining
  isCritical: boolean // less than 2 hours remaining
  formatted: string
  shortFormatted: string
}

/**
 * Hook to calculate countdown to a deadline
 * @param deadline - ISO date string or Date object for the deadline
 * @param updateInterval - How often to update in ms (default: 1000)
 */
export function useCountdown(
  deadline: string | Date | null | undefined,
  updateInterval = 1000
): CountdownResult | null {
  const deadlineDate = useMemo(() => {
    if (!deadline) return null
    return typeof deadline === 'string' ? new Date(deadline) : deadline
  }, [deadline])

  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    if (!deadlineDate) return

    const timer = setInterval(() => {
      setNow(new Date())
    }, updateInterval)

    return () => clearInterval(timer)
  }, [deadlineDate, updateInterval])

  if (!deadlineDate) return null

  const totalSeconds = Math.floor((deadlineDate.getTime() - now.getTime()) / 1000)
  const isExpired = totalSeconds <= 0

  if (isExpired) {
    return {
      days: 0,
      hours: 0,
      minutes: 0,
      seconds: 0,
      totalSeconds: 0,
      isExpired: true,
      isUrgent: true,
      isCritical: true,
      formatted: 'Expired',
      shortFormatted: 'Expired',
    }
  }

  const days = Math.floor(totalSeconds / (24 * 60 * 60))
  const hours = Math.floor((totalSeconds % (24 * 60 * 60)) / (60 * 60))
  const minutes = Math.floor((totalSeconds % (60 * 60)) / 60)
  const seconds = totalSeconds % 60

  const isUrgent = totalSeconds < 24 * 60 * 60 // less than 24 hours
  const isCritical = totalSeconds < 2 * 60 * 60 // less than 2 hours

  // Format: "2d 5h 30m" or "5h 30m 15s" if less than a day
  let formatted: string
  let shortFormatted: string

  if (days > 0) {
    formatted = `${days}d ${hours}h ${minutes}m`
    shortFormatted = `${days}d ${hours}h`
  } else if (hours > 0) {
    formatted = `${hours}h ${minutes}m ${seconds}s`
    shortFormatted = `${hours}h ${minutes}m`
  } else if (minutes > 0) {
    formatted = `${minutes}m ${seconds}s`
    shortFormatted = `${minutes}m`
  } else {
    formatted = `${seconds}s`
    shortFormatted = `${seconds}s`
  }

  return {
    days,
    hours,
    minutes,
    seconds,
    totalSeconds,
    isExpired,
    isUrgent,
    isCritical,
    formatted,
    shortFormatted,
  }
}

/**
 * Calculate deadline from claimed_at + estimated_hours
 */
export function calculateDeadlineFromEstimate(
  claimedAt: string | Date | null | undefined,
  estimatedHours: number | string | null | undefined
): Date | null {
  if (!claimedAt || !estimatedHours) return null

  const claimedDate = typeof claimedAt === 'string' ? new Date(claimedAt) : claimedAt
  const hours = typeof estimatedHours === 'string' ? parseFloat(estimatedHours) : estimatedHours

  if (isNaN(hours) || hours <= 0) return null

  return new Date(claimedDate.getTime() + hours * 60 * 60 * 1000)
}
