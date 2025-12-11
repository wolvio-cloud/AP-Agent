'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import StatusBadge from '@/components/invoices/StatusBadge'
import ProcessingTierBadge from '@/components/invoices/ProcessingTierBadge'
import ConfidenceRing from '@/components/invoices/ConfidenceRing'
import {
  ArrowLeft,
  FileText,
  Download,
  Zap,
  Calendar,
  Building2,
  Hash,
  DollarSign,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react'
import Link from 'next/link'

interface InvoiceDetail {
  id: string
  file_name: string
  file_url?: string
  status: string
  processing_tier?: string

  // Extracted fields
  vendor_name?: string
  vendor_address?: string
  vendor_tax_id?: string
  invoice_number?: string
  invoice_date?: string
  due_date?: string
  currency?: string
  payment_terms?: string
  subtotal?: number
  tax_amount?: number
  tax_rate?: number
  total_amount?: number
  line_items?: Array<{
    description: string
    quantity: number
    unit_price: number
    amount: number
  }>

  // Confidence scores
  overall_confidence?: number
  per_field_confidence?: Record<string, number>

  // Review info
  requires_review?: boolean
  review_priority?: string

  // Metadata
  created_at: string
  updated_at: string
  extracted_at?: string
  processing_history?: Array<{
    tier: string
    confidence: number
    timestamp: string
    processing_time_ms: number
  }>
}

function InvoiceDetailContent() {
  const router = useRouter()
  const params = useParams()
  const invoiceId = params?.id as string

  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (invoiceId) {
      loadInvoice()
    }
  }, [invoiceId])

  const loadInvoice = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const token = localStorage.getItem('access_token')
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/invoices/${invoiceId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setInvoice(data.data)
      } else {
        setError('Failed to load invoice')
      }
    } catch (err) {
      console.error('Failed to load invoice:', err)
      setError('Failed to load invoice')
    } finally {
      setIsLoading(false)
    }
  }

  const handleProcessInvoice = async () => {
    if (!invoice) return

    try {
      setIsProcessing(true)
      setError(null)
      const token = localStorage.getItem('access_token')
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/invoices/${invoiceId}/extract`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        // Reload invoice to show extraction results
        await loadInvoice()
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to process invoice')
      }
    } catch (err) {
      console.error('Failed to process invoice:', err)
      setError('Failed to process invoice')
    } finally {
      setIsProcessing(false)
    }
  }

  const formatCurrency = (amount: number, currency: string = 'INR') => {
    if (currency === 'INR') {
      return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    }
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return '—'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-400'
    if (confidence >= 0.95) return 'text-green-600'
    if (confidence >= 0.85) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getFieldConfidence = (field: string) => {
    return invoice?.per_field_confidence?.[field]
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading invoice...</p>
        </div>
      </div>
    )
  }

  if (error || !invoice) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <p className="text-gray-900 font-medium mb-2">Failed to load invoice</p>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/invoices')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Back to Invoices
          </button>
        </div>
      </div>
    )
  }

  const hasExtractionData = invoice.overall_confidence !== undefined && invoice.overall_confidence !== null
  const canProcess = invoice.status === 'uploaded' || invoice.status === 'error'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-[1600px] mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/invoices')}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition"
              >
                <ArrowLeft size={20} />
                Back
              </button>
              <div className="border-l border-gray-300 pl-4">
                <h1 className="text-xl font-bold">{invoice.file_name}</h1>
                <p className="text-sm text-gray-600">Invoice Details</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {invoice.file_url && (
                <a
                  href={invoice.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                >
                  <Download size={18} />
                  Download
                </a>
              )}
              {canProcess && (
                <button
                  onClick={handleProcessInvoice}
                  disabled={isProcessing}
                  className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="animate-spin" size={18} />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Zap size={18} />
                      Process with AI
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto p-8">
        {/* Status Bar */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">Status</p>
                <StatusBadge status={invoice.status} size="md" />
              </div>
              {invoice.processing_tier && (
                <div className="border-l border-gray-200 pl-6">
                  <p className="text-sm text-gray-600 mb-1">Processing Tier</p>
                  <ProcessingTierBadge tier={invoice.processing_tier} />
                </div>
              )}
              {invoice.requires_review && (
                <div className="border-l border-gray-200 pl-6">
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <AlertCircle className="text-yellow-600" size={16} />
                    <span className="text-sm font-medium text-yellow-800">
                      Requires Review ({invoice.review_priority} priority)
                    </span>
                  </div>
                </div>
              )}
            </div>

            {hasExtractionData && (
              <div>
                <ConfidenceRing
                  confidence={invoice.overall_confidence || 0}
                  size="lg"
                  showLabel={true}
                  label="Overall Confidence"
                />
              </div>
            )}
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Document Viewer */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText size={20} />
              Document Preview
            </h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center bg-gray-50">
              {invoice.file_url ? (
                <div className="space-y-4">
                  <FileText className="mx-auto text-gray-400" size={64} />
                  <div>
                    <p className="text-gray-900 font-medium">{invoice.file_name}</p>
                    <p className="text-sm text-gray-600 mt-1">Click download to view full document</p>
                  </div>
                  <a
                    href={invoice.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    <Download size={18} />
                    Open Document
                  </a>
                </div>
              ) : (
                <div>
                  <FileText className="mx-auto text-gray-400 mb-4" size={64} />
                  <p className="text-gray-600">Document preview not available</p>
                </div>
              )}
            </div>

            {/* Processing History */}
            {invoice.processing_history && invoice.processing_history.length > 0 && (
              <div className="mt-6">
                <h3 className="text-md font-semibold mb-3 flex items-center gap-2">
                  <Clock size={18} />
                  Processing History
                </h3>
                <div className="space-y-3">
                  {invoice.processing_history.map((entry, index) => (
                    <div key={index} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex-shrink-0">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          entry.confidence >= 0.95 ? 'bg-green-100' :
                          entry.confidence >= 0.85 ? 'bg-yellow-100' :
                          'bg-red-100'
                        }`}>
                          <span className={`text-sm font-bold ${
                            entry.confidence >= 0.95 ? 'text-green-600' :
                            entry.confidence >= 0.85 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {Math.round(entry.confidence * 100)}%
                          </span>
                        </div>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {entry.tier.toUpperCase()} - {entry.processing_time_ms}ms
                        </p>
                        <p className="text-xs text-gray-600">
                          {formatDate(entry.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right: Extracted Data */}
          <div className="space-y-6">
            {!hasExtractionData ? (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <Zap className="mx-auto text-gray-400 mb-4" size={48} />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No extraction data yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Click &quot;Process with AI&quot; to extract data from this invoice using our 4-tier AI pipeline.
                </p>
                {canProcess && (
                  <button
                    onClick={handleProcessInvoice}
                    disabled={isProcessing}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="animate-spin" size={18} />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Zap size={18} />
                        Process with AI
                      </>
                    )}
                  </button>
                )}
              </div>
            ) : (
              <>
                {/* Vendor Information */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Building2 size={20} />
                    Vendor Information
                  </h2>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium text-gray-700">Vendor Name</label>
                        {getFieldConfidence('vendor_name') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('vendor_name'))}`}>
                            {Math.round((getFieldConfidence('vendor_name') || 0) * 100)}% confident
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900">{invoice.vendor_name || '—'}</p>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium text-gray-700">Address</label>
                        {getFieldConfidence('vendor_address') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('vendor_address'))}`}>
                            {Math.round((getFieldConfidence('vendor_address') || 0) * 100)}% confident
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900 text-sm">{invoice.vendor_address || '—'}</p>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium text-gray-700">Tax ID / GSTIN</label>
                        {getFieldConfidence('vendor_tax_id') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('vendor_tax_id'))}`}>
                            {Math.round((getFieldConfidence('vendor_tax_id') || 0) * 100)}% confident
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900 font-mono">{invoice.vendor_tax_id || '—'}</p>
                    </div>
                  </div>
                </div>

                {/* Invoice Details */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Hash size={20} />
                    Invoice Details
                  </h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium text-gray-700">Invoice Number</label>
                        {getFieldConfidence('invoice_number') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('invoice_number'))}`}>
                            {Math.round((getFieldConfidence('invoice_number') || 0) * 100)}%
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900 font-mono">{invoice.invoice_number || '—'}</p>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium text-gray-700">Currency</label>
                      </div>
                      <p className="text-gray-900">{invoice.currency || '—'}</p>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium text-gray-700">Invoice Date</label>
                        {getFieldConfidence('invoice_date') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('invoice_date'))}`}>
                            {Math.round((getFieldConfidence('invoice_date') || 0) * 100)}%
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900">{formatDate(invoice.invoice_date)}</p>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium text-gray-700">Due Date</label>
                        {getFieldConfidence('due_date') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('due_date'))}`}>
                            {Math.round((getFieldConfidence('due_date') || 0) * 100)}%
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900">{formatDate(invoice.due_date)}</p>
                    </div>
                    <div className="col-span-2">
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-sm font-medium text-gray-700">Payment Terms</label>
                      </div>
                      <p className="text-gray-900">{invoice.payment_terms || '—'}</p>
                    </div>
                  </div>
                </div>

                {/* Financial Summary */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <DollarSign size={20} />
                    Financial Summary
                  </h2>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-700">Subtotal</span>
                        {getFieldConfidence('subtotal') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('subtotal'))}`}>
                            {Math.round((getFieldConfidence('subtotal') || 0) * 100)}%
                          </span>
                        )}
                      </div>
                      <span className="font-medium text-gray-900">
                        {invoice.subtotal ? formatCurrency(invoice.subtotal, invoice.currency) : '—'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-700">Tax ({invoice.tax_rate ? `${invoice.tax_rate}%` : '—'})</span>
                        {getFieldConfidence('tax_amount') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('tax_amount'))}`}>
                            {Math.round((getFieldConfidence('tax_amount') || 0) * 100)}%
                          </span>
                        )}
                      </div>
                      <span className="font-medium text-gray-900">
                        {invoice.tax_amount ? formatCurrency(invoice.tax_amount, invoice.currency) : '—'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-semibold text-gray-900">Total</span>
                        {getFieldConfidence('total_amount') && (
                          <span className={`text-xs font-medium ${getConfidenceColor(getFieldConfidence('total_amount'))}`}>
                            {Math.round((getFieldConfidence('total_amount') || 0) * 100)}%
                          </span>
                        )}
                      </div>
                      <span className="text-2xl font-bold text-blue-600">
                        {invoice.total_amount ? formatCurrency(invoice.total_amount, invoice.currency) : '—'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Line Items */}
                {invoice.line_items && invoice.line_items.length > 0 && (
                  <div className="bg-white rounded-lg shadow-sm p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-lg font-semibold flex items-center gap-2">
                        Line Items
                      </h2>
                      {getFieldConfidence('line_items') && (
                        <span className={`text-sm font-medium ${getConfidenceColor(getFieldConfidence('line_items'))}`}>
                          {Math.round((getFieldConfidence('line_items') || 0) * 100)}% confident
                        </span>
                      )}
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {invoice.line_items.map((item, index) => (
                            <tr key={index}>
                              <td className="px-4 py-3 text-sm text-gray-900">{item.description}</td>
                              <td className="px-4 py-3 text-sm text-right text-gray-900">{item.quantity}</td>
                              <td className="px-4 py-3 text-sm text-right text-gray-900">
                                {formatCurrency(item.unit_price, invoice.currency)}
                              </td>
                              <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                                {formatCurrency(item.amount, invoice.currency)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default function InvoiceDetailPage() {
  return (
    <ProtectedRoute>
      <InvoiceDetailContent />
    </ProtectedRoute>
  )
}
