import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  wallet_address: string
  name: string
  country: string
  bio?: string
  skills?: string[]
  id_verified?: boolean
  reputation_score?: number
  reputation_tier: string
  tasks_completed: number
  tasks_approved?: number
  is_admin: boolean
  is_banned: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  setUser: (user: User) => void
  setToken: (token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: true }),
      setToken: (token) => set({ token }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'flow-auth',
    }
  )
)
