import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

import { getMe } from "@/api/endpoints"
import { clearTokens, getTokens, setTokens as saveTokens } from "@/api/client"
import type { User } from "@/api/types"

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (access: string, refresh: string, user: User) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const { access } = getTokens()
    if (!access) {
      setIsLoading(false)
      return
    }
    getMe()
      .then(setUser)
      .catch(() => clearTokens())
      .finally(() => setIsLoading(false))
  }, [])

  function login(access: string, refresh: string, newUser: User) {
    saveTokens(access, refresh)
    setUser(newUser)
  }

  function logout() {
    clearTokens()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: user !== null, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
