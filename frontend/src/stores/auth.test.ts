import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore, User } from './auth'

const mockUser: User = {
  id: 'user-123',
  wallet_address: '0x1234567890abcdef1234567890abcdef12345678',
  name: 'Test User',
  country: 'US',
  bio: 'Test bio',
  skills: ['research', 'writing'],
  id_verified: true,
  reputation_score: 100,
  reputation_tier: 'gold',
  tasks_completed: 10,
  tasks_approved: 8,
  is_admin: false,
  is_banned: false,
}

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
    })
    localStorage.clear()
  })

  it('TC-FE-006: setUser updates user and isAuthenticated', () => {
    const { setUser } = useAuthStore.getState()

    setUser(mockUser)

    const state = useAuthStore.getState()
    expect(state.user).toEqual(mockUser)
    expect(state.isAuthenticated).toBe(true)
  })

  it('TC-FE-007: logout clears all auth state', () => {
    const { setUser, setToken, logout } = useAuthStore.getState()

    setUser(mockUser)
    setToken('test-token')

    let state = useAuthStore.getState()
    expect(state.user).not.toBeNull()
    expect(state.token).toBe('test-token')

    logout()

    state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('TC-FE-008: Auth state persists to localStorage', () => {
    const { setUser, setToken } = useAuthStore.getState()

    setUser(mockUser)
    setToken('persist-token')

    const stored = localStorage.getItem('flow-auth')
    expect(stored).not.toBeNull()

    const parsed = JSON.parse(stored!)
    expect(parsed.state.user).toEqual(mockUser)
    expect(parsed.state.token).toBe('persist-token')
    expect(parsed.state.isAuthenticated).toBe(true)
  })

  it('setToken updates token in state', () => {
    const { setToken } = useAuthStore.getState()

    setToken('new-token')

    const state = useAuthStore.getState()
    expect(state.token).toBe('new-token')
  })

  it('initial state is unauthenticated', () => {
    const state = useAuthStore.getState()

    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })
})
