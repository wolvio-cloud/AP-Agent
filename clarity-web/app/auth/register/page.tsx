'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { Eye, EyeOff, Loader2, CheckCircle2, XCircle, FileText, AlertCircle } from 'lucide-react'

// Validation schema
const registerSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Invalid email address'),
  company_name: z.string().min(1, 'Company name is required'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Za-z]/, 'Password must contain at least one letter')
    .regex(/\d/, 'Password must contain at least one number'),
  confirm_password: z.string(),
  accept_terms: z.boolean().refine((val) => val === true, {
    message: 'You must accept the terms and conditions',
  }),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
})

type RegisterFormData = z.infer<typeof registerSchema>

// Password strength indicator
function getPasswordStrength(password: string): { strength: number; label: string; color: string } {
  if (!password) return { strength: 0, label: '', color: '' }

  let strength = 0
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^A-Za-z0-9]/.test(password)) strength++

  if (strength <= 2) return { strength, label: 'Weak', color: 'bg-red-500' }
  if (strength <= 3) return { strength, label: 'Medium', color: 'bg-yellow-500' }
  return { strength, label: 'Strong', color: 'bg-green-500' }
}

export default function RegisterPage() {
  const { register: registerUser } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [passwordValue, setPasswordValue] = useState('')

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const password = watch('password', '')
  const passwordStrength = getPasswordStrength(password)

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true)
    setError(null)

    try {
      const { confirm_password, accept_terms, ...registerData } = data
      await registerUser(registerData)
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4 shadow-medium">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            Create Account
          </h1>
          <p className="text-secondary-600">
            Start automating your invoice processing today
          </p>
        </div>

        {/* Register Card */}
        <div className="bg-white rounded-2xl shadow-soft border border-secondary-100 p-8 animate-scale-in">
          {error && (
            <div className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-xl flex items-start gap-3 animate-slide-in">
              <AlertCircle className="w-5 h-5 text-danger-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-danger-900">Registration Failed</p>
                <p className="text-sm text-danger-700 mt-0.5">{error}</p>
              </div>
            </div>
          )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium mb-2">
                First Name
              </label>
              <input
                {...register('first_name')}
                id="first_name"
                type="text"
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.first_name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="John"
                disabled={isLoading}
              />
              {errors.first_name && (
                <p className="mt-1 text-xs text-red-600">{errors.first_name.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="last_name" className="block text-sm font-medium mb-2">
                Last Name
              </label>
              <input
                {...register('last_name')}
                id="last_name"
                type="text"
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.last_name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Doe"
                disabled={isLoading}
              />
              {errors.last_name && (
                <p className="mt-1 text-xs text-red-600">{errors.last_name.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              Email
            </label>
            <input
              {...register('email')}
              id="email"
              type="email"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="you@example.com"
              disabled={isLoading}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="company_name" className="block text-sm font-medium mb-2">
              Company Name
            </label>
            <input
              {...register('company_name')}
              id="company_name"
              type="text"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.company_name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Acme Inc"
              disabled={isLoading}
            />
            {errors.company_name && (
              <p className="mt-1 text-sm text-red-600">{errors.company_name.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              Password
            </label>
            <div className="relative">
              <input
                {...register('password')}
                id="password"
                type={showPassword ? 'text' : 'password'}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10 ${
                  errors.password ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="••••••••"
                disabled={isLoading}
                onChange={(e) => setPasswordValue(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {password && (
              <div className="mt-2">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-600">Password strength:</span>
                  <span className={`font-medium ${
                    passwordStrength.label === 'Weak' ? 'text-red-600' :
                    passwordStrength.label === 'Medium' ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {passwordStrength.label}
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${passwordStrength.color}`}
                    style={{ width: `${(passwordStrength.strength / 5) * 100}%` }}
                  />
                </div>
              </div>
            )}
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium mb-2">
              Confirm Password
            </label>
            <div className="relative">
              <input
                {...register('confirm_password')}
                id="confirm_password"
                type={showConfirmPassword ? 'text' : 'password'}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10 ${
                  errors.confirm_password ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="••••••••"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {errors.confirm_password && (
              <p className="mt-1 text-sm text-red-600">{errors.confirm_password.message}</p>
            )}
          </div>

          <div className="flex items-start">
            <input
              {...register('accept_terms')}
              id="accept_terms"
              type="checkbox"
              className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              disabled={isLoading}
            />
            <label htmlFor="accept_terms" className="ml-2 text-sm text-gray-600">
              I agree to the{' '}
              <a href="#" className="text-blue-600 hover:underline">
                Terms and Conditions
              </a>{' '}
              and{' '}
              <a href="#" className="text-blue-600 hover:underline">
                Privacy Policy
              </a>
            </label>
          </div>
          {errors.accept_terms && (
            <p className="text-sm text-red-600">{errors.accept_terms.message}</p>
          )}

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
                Creating account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Sign In Link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-secondary-600">
            Already have an account?{' '}
            <Link
              href="/auth/login"
              className="font-medium text-primary-600 hover:text-primary-700 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center text-sm text-secondary-500 animate-fade-in">
        <p>
          By creating an account, you agree to our Terms of Service
        </p>
      </div>
    </div>
    </div>
  )
}
