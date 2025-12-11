'use client'

import { useState, useEffect, createContext, useContext, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, User, Organization, RegisterData, LoginData } from '@/lib/api'

interface AuthContextType {
  user: User | null
  organization: Organization | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (data: LoginData) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [organization, setOrganization] = useState<Organization | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Load user on mount
  useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      if (apiClient.isAuthenticated()) {
        const response = await apiClient.getCurrentUser()
        setUser(response.data.user)
        setOrganization(response.data.organization)
      }
    } catch (error) {
      console.error('Failed to load user:', error)
      setUser(null)
      setOrganization(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (data: LoginData) => {
    try {
      const response = await apiClient.login(data)
      setUser(response.data.user)
      setOrganization(response.data.organization)
      router.push('/dashboard')
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  const register = async (data: RegisterData) => {
    try {
      const response = await apiClient.register(data)
      setUser(response.data.user)
      setOrganization(response.data.organization)
      router.push('/dashboard')
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed')
    }
  }

  const logout = async () => {
    try {
      await apiClient.logout()
    } finally {
      setUser(null)
      setOrganization(null)
      router.push('/auth/login')
    }
  }

  const refreshUser = async () => {
    await loadUser()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        organization,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
