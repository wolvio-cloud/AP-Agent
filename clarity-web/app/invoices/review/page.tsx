'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import StatusBadge from '@/components/invoices/StatusBadge'
import ProcessingTierBadge from '@/components/invoices/ProcessingTierBadge'
import ConfidenceRing from '@/components/invoices/ConfidenceRing'
import {
  AlertCircle,
  FileText,
  ArrowLeft,
  Filter,
  TrendingUp,
  Clock,
  ChevronRight,
  Loader2
} from 'lucide-react'
import Link from 'next/link'

interface InvoiceReview {
  id: string
  file_name: string
  status: string
  processing_tier?: string
  vendor_name?: string
  invoice_number?: string
  total_amount?: number
  currency?: string
  overall_confidence?: number
  requires_review: boolean
  review_priority: string
  created_at: string
  extracted_at?: string
}

function ReviewQueueContent() {
  const router = useRouter()
  const [invoices, setInvoices] = useState<InvoiceReview[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [stats, setStats] = useState({
    total: 0,
    high: 0,
    medium: 0,
    low: 0
  })

  useEffect(() => {
    loadReviewQueue()
  }, [priorityFilter])

  const loadReviewQueue = async () => {
    try {
      setIsLoading(true)
      const token = localStorage.getItem('access_token')
      const url = new URL(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/invoices/queue/review`)

      if (priorityFilter !== 'all') {
        url.searchParams.append('priority', priorityFilter)
      }

      const response = await fetch(url.toString(), {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setInvoices(data.data || [])

        // Calculate stats
        const allInvoices = data.data || []
        setStats({
          total: allInvoices.length,
          high: allInvoices.filter((inv: InvoiceReview) => inv.review_priority === 'high').length,
          medium: allInvoices.filter((inv: InvoiceReview) => inv.review_priority === 'medium').length,
          low: allInvoices.filter((inv: InvoiceReview) => inv.review_priority === 'low').length,
        })
      }
    } catch (error) {
      console.error('Failed to load review queue:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatCurrency = (amount: number, currency: string = 'INR') => {
    if (currency === 'INR') {
      return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    }
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getPriorityBadge = (priority: string) => {
    const config = {
      high: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200', label: 'High Priority' },
      medium: { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-200', label: 'Medium Priority' },
      low: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200', label: 'Low Priority' },
    }
    const style = config[priority as keyof typeof config] || config.low

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${style.bg} ${style.text} ${style.border}`}>
        <div className={`w-1.5 h-1.5 rounded-full ${style.text.replace('text', 'bg')}`} />
        {style.label}
      </span>
    )
  }

  const getTimeSince = (dateString?: string) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffDays > 0) return `${diffDays}d ago`
    if (diffHours > 0) return `${diffHours}h ago`
    if (diffMins > 0) return `${diffMins}m ago`
    return 'Just now'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-[1600px] mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/invoices"
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition"
              >
                <ArrowLeft size={20} />
                Back
              </Link>
              <div className="border-l border-gray-300 pl-4">
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <AlertCircle className="text-yellow-600" size={28} />
                  Review Queue
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  Invoices requiring human review due to low confidence scores
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto p-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-gray-400">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Reviews</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
              </div>
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                <FileText className="text-gray-600" size={24} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Priority</p>
                <p className="text-3xl font-bold text-red-600 mt-2">{stats.high}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <TrendingUp className="text-red-600" size={24} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Medium Priority</p>
                <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.medium}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <Clock className="text-yellow-600" size={24} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Low Priority</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">{stats.low}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <AlertCircle className="text-blue-600" size={24} />
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex items-center gap-4">
            <Filter className="text-gray-400" size={20} />
            <div className="flex gap-2">
              <button
                onClick={() => setPriorityFilter('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  priorityFilter === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All ({stats.total})
              </button>
              <button
                onClick={() => setPriorityFilter('high')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  priorityFilter === 'high'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                High ({stats.high})
              </button>
              <button
                onClick={() => setPriorityFilter('medium')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  priorityFilter === 'medium'
                    ? 'bg-yellow-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Medium ({stats.medium})
              </button>
              <button
                onClick={() => setPriorityFilter('low')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  priorityFilter === 'low'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Low ({stats.low})
              </button>
            </div>
          </div>
        </div>

        {/* Invoices List */}
        {isLoading ? (
          <div className="text-center py-12">
            <Loader2 className="animate-spin h-12 w-12 border-b-2 text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading review queue...</p>
          </div>
        ) : invoices.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="text-green-600" size={32} />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">All clear!</h3>
            <p className="text-gray-600">
              No invoices require review at this time. Great job!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {invoices.map((invoice) => (
              <div
                key={invoice.id}
                onClick={() => router.push(`/invoices/${invoice.id}`)}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition cursor-pointer border border-gray-200 hover:border-blue-300"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between gap-6">
                    {/* Left: Invoice Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-3">
                        <FileText className="text-gray-400 flex-shrink-0" size={24} />
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg font-semibold text-gray-900 truncate">
                            {invoice.file_name}
                          </h3>
                          <div className="flex items-center gap-2 mt-1">
                            <StatusBadge status={invoice.status} size="sm" />
                            {invoice.processing_tier && (
                              <ProcessingTierBadge tier={invoice.processing_tier} />
                            )}
                            {getPriorityBadge(invoice.review_priority)}
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Vendor</p>
                          <p className="text-sm font-medium text-gray-900">
                            {invoice.vendor_name || <span className="text-gray-400">Not extracted</span>}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Invoice #</p>
                          <p className="text-sm font-medium text-gray-900 font-mono">
                            {invoice.invoice_number || <span className="text-gray-400">—</span>}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Amount</p>
                          <p className="text-sm font-medium text-gray-900">
                            {invoice.total_amount
                              ? formatCurrency(invoice.total_amount, invoice.currency)
                              : <span className="text-gray-400">—</span>
                            }
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Extracted</p>
                          <p className="text-sm font-medium text-gray-900">
                            {getTimeSince(invoice.extracted_at)}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Right: Confidence Score */}
                    <div className="flex items-center gap-6">
                      <div className="text-center">
                        <ConfidenceRing
                          confidence={invoice.overall_confidence || 0}
                          size="md"
                          showLabel={false}
                        />
                        <p className="text-xs text-gray-600 mt-2 font-medium">Confidence</p>
                      </div>
                      <ChevronRight className="text-gray-400" size={24} />
                    </div>
                  </div>
                </div>

                {/* Warning Banner for High Priority */}
                {invoice.review_priority === 'high' && (
                  <div className="bg-red-50 border-t border-red-100 px-6 py-3 flex items-center gap-2">
                    <AlertCircle className="text-red-600 flex-shrink-0" size={16} />
                    <p className="text-sm text-red-800">
                      <span className="font-semibold">Action required:</span> This invoice has very low confidence and needs immediate review.
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default function ReviewQueuePage() {
  return (
    <ProtectedRoute>
      <ReviewQueueContent />
    </ProtectedRoute>
  )
}
