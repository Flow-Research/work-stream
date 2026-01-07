import { AxiosError } from 'axios'
import toast from 'react-hot-toast'

interface ApiErrorResponse {
  detail?: string | { msg: string }[]
  message?: string
}

export function extractErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiErrorResponse | undefined
    
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        return data.detail
      }
      if (Array.isArray(data.detail) && data.detail[0]?.msg) {
        return data.detail[0].msg
      }
    }
    
    if (data?.message) {
      return data.message
    }
    
    switch (error.response?.status) {
      case 401:
        return 'Session expired. Please reconnect your wallet.'
      case 403:
        return 'You do not have permission to perform this action.'
      case 404:
        return 'The requested resource was not found.'
      case 422:
        return 'Invalid data provided. Please check your input.'
      case 429:
        return 'Too many requests. Please wait a moment and try again.'
      case 500:
      case 502:
      case 503:
        return 'Server error. Please try again later.'
      default:
        break
    }
    
    if (error.code === 'ERR_NETWORK') {
      return 'Network error. Please check your connection.'
    }
    
    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Please try again.'
    }
  }
  
  if (error instanceof Error) {
    return error.message
  }
  
  return 'An unexpected error occurred. Please try again.'
}

export function useApiError() {
  const showError = (error: unknown) => {
    const message = extractErrorMessage(error)
    toast.error(message)
  }
  
  return { showError, extractErrorMessage }
}
