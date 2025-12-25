import axios, { AxiosInstance, AxiosError } from 'axios'

// Types
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  organization_id: string
  is_active: boolean
}

export interface Organization {
  id: string
  name: string
  slug: string
  email: string
  country: string
  currency: string
}

export interface AuthResponse {
  success: boolean
  data: {
    access_token: string
    token_type: string
    user: User
    organization: Organization
  }
  message: string
}

export interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
  company_name: string
}

export interface LoginData {
  email: string
  password: string
}

// API Client
class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add token to requests if available
    this.client.interceptors.request.use((config) => {
      const token = this.getToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Handle 401 errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Clear token and redirect to login
          this.removeToken()
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // Token management
  private getToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
  }

  private removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
  }

  // Auth endpoints
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/v1/auth/register', data)
    if (response.data.success && response.data.data.access_token) {
      this.setToken(response.data.data.access_token)
    }
    return response.data
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/v1/auth/login', data)
    if (response.data.success && response.data.data.access_token) {
      this.setToken(response.data.data.access_token)
    }
    return response.data
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/api/v1/auth/logout')
    } finally {
      this.removeToken()
    }
  }

  async getCurrentUser(): Promise<AuthResponse> {
    const response = await this.client.get<AuthResponse>('/api/v1/auth/me')
    return response.data
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.getToken()
  }

  // Invoice endpoints
  async uploadInvoice(file: File): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await this.client.post('/api/v1/invoices/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async getInvoices(): Promise<any> {
    const response = await this.client.get('/api/v1/invoices')
    return response.data
  }

  async getInvoice(id: string): Promise<any> {
    const response = await this.client.get(`/api/v1/invoices/${id}`)
    return response.data
  }

  async updateInvoice(id: string, data: any): Promise<any> {
    const response = await this.client.put(`/api/v1/invoices/${id}`, data)
    return response.data
  }

  async deleteInvoice(id: string): Promise<any> {
    const response = await this.client.delete(`/api/v1/invoices/${id}`)
    return response.data
  }

  // QuickBooks export endpoints
  async exportInvoiceIIF(id: string): Promise<Blob> {
    const response = await this.client.get(`/api/v1/quickbooks/export/iif/${id}`, {
      responseType: 'blob',
    })
    return response.data
  }

  async exportInvoicesIIFBatch(invoiceIds: string[]): Promise<Blob> {
    const response = await this.client.post('/api/v1/quickbooks/export/iif/batch',
      { invoice_ids: invoiceIds },
      { responseType: 'blob' }
    )
    return response.data
  }

  async exportInvoicesCSV(): Promise<Blob> {
    const response = await this.client.get('/api/v1/quickbooks/export/csv', {
      responseType: 'blob',
    })
    return response.data
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
