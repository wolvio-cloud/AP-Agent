'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { Eye, EyeOff, Loader2, FileText, AlertCircle, CheckCircle2 } from 'lucide-react'

// Validation schema
const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const { login } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setError(null)
    setSuccess(false)

    try {
      await login(data)
      setSuccess(true)
    } catch (err: any) {
      setError(err.message || 'Invalid email or password. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4 shadow-medium">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            Welcome Back
          </h1>
          <p className="text-secondary-600">
            Sign in to your ClarityAP account
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-soft border border-secondary-100 p-8 animate-scale-in">
          {/* Alert Messages */}
          {error && (
            <div className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-xl flex items-start gap-3 animate-slide-in">
              <AlertCircle className="w-5 h-5 text-danger-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-danger-900">Login Failed</p>
                <p className="text-sm text-danger-700 mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-success-50 border border-success-200 rounded-xl flex items-start gap-3 animate-slide-in">
              <CheckCircle2 className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-success-900">Login Successful</p>
                <p className="text-sm text-success-700 mt-0.5">Redirecting to dashboard...</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-secondary-700 mb-2">
                Email Address
              </label>
              <input
                {...register('email')}
                id="email"
                type="email"
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-all ${
                  errors.email
                    ? 'border-danger-300 focus:ring-danger-500 focus:border-danger-500'
                    : 'border-secondary-300 focus:ring-primary-500 focus:border-primary-500'
                } bg-white text-secondary-900 placeholder-secondary-400`}
                placeholder="you@company.com"
                disabled={isLoading}
              />
              {errors.email && (
                <p className="mt-1.5 text-sm text-danger-600 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-secondary-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  {...register('password')}
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-all pr-12 ${
                    errors.password
                      ? 'border-danger-300 focus:ring-danger-500 focus:border-danger-500'
                      : 'border-secondary-300 focus:ring-primary-500 focus:border-primary-500'
                  } bg-white text-secondary-900 placeholder-secondary-400`}
                  placeholder="••••••••"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-secondary-500 hover:text-secondary-700 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1.5 text-sm text-danger-600 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Remember Me */}
            <div className="flex items-center">
              <input
                id="remember"
                type="checkbox"
                className="w-4 h-4 border-secondary-300 rounded text-primary-600 focus:ring-primary-500 focus:ring-2"
              />
              <label htmlFor="remember" className="ml-2 text-sm text-secondary-700">
                Remember me for 30 days
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl
                       focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                       disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-soft hover:shadow-medium
                       flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-secondary-600">
              Don't have an account?{' '}
              <Link
                href="/auth/register"
                className="font-medium text-primary-600 hover:text-primary-700 transition-colors"
              >
                Create account
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-secondary-500 animate-fade-in">
          <p>
            Protected by enterprise-grade security
          </p>
        </div>
      </div>
    </div>
  )
}
