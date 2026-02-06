import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../api/auth'
import { User } from '../types'

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean

  login: (username: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        const data = await authApi.login({ username, password })
        set({
          token: data.access_token,
          isAuthenticated: true,
        })
        await authApi.getMe().then(res => {
          set({ user: { ...res, role: res.role as User['role'] } })
        })
      },

      logout: () => {
        set({
          token: null,
          user: null,
          isAuthenticated: false,
        })
      },

      checkAuth: async () => {
        const token = useAuthStore.getState().token
        if (token) {
          try {
            const res = await authApi.getMe()
            set({ user: { ...res, role: res.role as User['role'] } })
          } catch {
            set({
              token: null,
              user: null,
              isAuthenticated: false,
            })
          }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
