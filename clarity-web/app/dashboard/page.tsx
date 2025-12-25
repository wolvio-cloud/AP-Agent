'use client'

import { useState, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import { useDropzone } from 'react-dropzone'
import { apiClient } from '@/lib/api'
import {
  FileText, Upload, Save, Trash2, Download, LogOut,
  AlertCircle, CheckCircle2, Loader2, X, Plus, Edit2
} from 'lucide-react'

// Global currency options
const CURRENCIES = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'INR', symbol: '₹', name: 'Indian Rupee' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
  { code: 'SGD', symbol: 'S$', name: 'Singapore Dollar' },
  { code: 'AED', symbol: 'د.إ', name: 'UAE Dirham' },
]

// Tax types for different regions
const TAX_TYPES = [
  { value: 'GST', label: 'GST (India)', region: 'India' },
  { value: 'VAT', label: 'VAT (EU/UK)', region: 'Europe' },
  { value: 'Sales Tax', label: 'Sales Tax (US)', region: 'US' },
  { value: 'Service Tax', label: 'Service Tax', region: 'Global' },
  { value: 'None', label: 'No Tax', region: 'Global' },
]

interface LineItem {
  description: string
  quantity: number
  rate: number
  amount: number
}

interface InvoiceData {
  id?: string
  vendor_name: string
  invoice_number: string
  invoice_date: string
  due_date: string
  subtotal: number
  tax_amount: number
  tax_type: string
  tax_percentage: number
  total_amount: number
  currency: string
  line_items: LineItem[]
  notes?: string
  // India-specific
  gstin?: string
  pan?: string
  // EU-specific
  vat_number?: string
}

function DashboardContent() {
  const { user, organization, logout } = useAuth()

  // Upload state
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)

  // Invoice state
  const [invoice, setInvoice] = useState<InvoiceData | null>(null)
  const [extracting, setExtracting] = useState(false)
  const [saving, setSaving] = useState(false)
  const [exporting, setExporting] = useState(false)

  // Form state
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState<InvoiceData | null>(null)

  // File upload handler
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setUploadError(null)
    setUploadSuccess(false)
    setExtracting(true)

    try {
      const result = await apiClient.uploadInvoice(file)
      setInvoice(result)
      setFormData(result.extracted_json || {})
      setUploadSuccess(true)
      setEditMode(true)
    } catch (error: any) {
      setUploadError(error.response?.data?.detail || 'Failed to upload invoice. Please try again.')
    } finally {
      setUploading(false)
      setExtracting(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    disabled: uploading,
  })

  // Save invoice handler
  const handleSave = async () => {
    if (!invoice?.id || !formData) return

    setSaving(true)
    try {
      await apiClient.updateInvoice(invoice.id, { extracted_json: formData })
      setInvoice({ ...invoice, extracted_json: formData })
      alert('Invoice saved successfully!')
    } catch (error) {
      alert('Failed to save invoice')
    } finally {
      setSaving(false)
    }
  }

  // Delete invoice handler
  const handleDelete = async () => {
    if (!invoice?.id) return
    if (!confirm('Are you sure you want to delete this invoice?')) return

    try {
      await apiClient.deleteInvoice(invoice.id)
      setInvoice(null)
      setFormData(null)
      setEditMode(false)
      alert('Invoice deleted successfully!')
    } catch (error) {
      alert('Failed to delete invoice')
    }
  }

  // Export to QuickBooks
  const handleExport = async () => {
    if (!invoice?.id) return

    setExporting(true)
    try {
      const blob = await apiClient.exportInvoiceIIF(invoice.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `invoice_${invoice.invoice_number || invoice.id}.iif`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      alert('Invoice exported successfully! Import the IIF file into QuickBooks.')
    } catch (error) {
      alert('Failed to export invoice')
    } finally {
      setExporting(false)
    }
  }

  // Add line item
  const addLineItem = () => {
    if (!formData) return
    const newItem: LineItem = { description: '', quantity: 1, rate: 0, amount: 0 }
    setFormData({
      ...formData,
      line_items: [...(formData.line_items || []), newItem],
    })
  }

  // Remove line item
  const removeLineItem = (index: number) => {
    if (!formData) return
    const items = [...(formData.line_items || [])]
    items.splice(index, 1)
    setFormData({ ...formData, line_items: items })
  }

  // Update line item
  const updateLineItem = (index: number, field: keyof LineItem, value: any) => {
    if (!formData) return
    const items = [...(formData.line_items || [])]
    items[index] = { ...items[index], [field]: value }

    // Auto-calculate amount
    if (field === 'quantity' || field === 'rate') {
      items[index].amount = items[index].quantity * items[index].rate
    }

    setFormData({ ...formData, line_items: items })

    // Recalculate subtotal
    const subtotal = items.reduce((sum, item) => sum + item.amount, 0)
    const total = subtotal + (formData.tax_amount || 0)
    setFormData({ ...formData, line_items: items, subtotal, total_amount: total })
  }

  // Update form field
  const updateField = (field: keyof InvoiceData, value: any) => {
    if (!formData) return
    setFormData({ ...formData, [field]: value })

    // Auto-recalculate total if tax changes
    if (field === 'tax_amount') {
      setFormData({ ...formData, [field]: value, total_amount: (formData.subtotal || 0) + parseFloat(value || 0) })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Modern Header */}
      <header className="bg-white border-b border-secondary-200 shadow-soft">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-xl">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-secondary-900">ClarityAP</h1>
              <p className="text-sm text-secondary-600">{organization?.name}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <p className="text-sm font-medium text-secondary-900">{user?.first_name} {user?.last_name}</p>
              <p className="text-xs text-secondary-600">{user?.email}</p>
            </div>
            <button
              onClick={logout}
              className="p-2.5 text-secondary-600 hover:text-danger-600 hover:bg-danger-50 rounded-xl transition-all"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {!invoice ? (
          // Upload Zone
          <div className="animate-fade-in">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-secondary-900 mb-2">Upload Invoice</h2>
              <p className="text-secondary-600">
                Upload invoices from anywhere in the world. Supports India (GST), US (Sales Tax), EU/UK (VAT), and more.
              </p>
            </div>

            {/* Upload Dropzone */}
            <div
              {...getRootProps()}
              className={`
                relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all
                ${isDragActive
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-secondary-300 hover:border-primary-400 hover:bg-primary-50/50'
                }
                ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <input {...getInputProps()} />

              <div className="flex flex-col items-center gap-4">
                <div className={`
                  w-20 h-20 rounded-full flex items-center justify-center transition-all
                  ${uploading ? 'bg-primary-600' : 'bg-primary-100'}
                `}>
                  {uploading ? (
                    <Loader2 className="w-10 h-10 text-white animate-spin" />
                  ) : (
                    <Upload className="w-10 h-10 text-primary-600" />
                  )}
                </div>

                <div>
                  <p className="text-xl font-semibold text-secondary-900 mb-2">
                    {uploading ? 'Uploading & Extracting...' :
                     isDragActive ? 'Drop invoice here' :
                     'Drag & drop invoice here'}
                  </p>
                  <p className="text-sm text-secondary-600 mb-4">
                    or click to browse files
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center text-xs text-secondary-500">
                    <span className="px-3 py-1 bg-secondary-100 rounded-full">PDF</span>
                    <span className="px-3 py-1 bg-secondary-100 rounded-full">JPG</span>
                    <span className="px-3 py-1 bg-secondary-100 rounded-full">PNG</span>
                    <span className="px-3 py-1 bg-secondary-100 rounded-full">Max 10MB</span>
                  </div>
                </div>

                {extracting && (
                  <div className="mt-4 text-sm text-primary-700 font-medium">
                    🔍 AI is extracting invoice data... (3-5 seconds)
                  </div>
                )}
              </div>
            </div>

            {/* Upload Status Messages */}
            {uploadError && (
              <div className="mt-6 p-4 bg-danger-50 border border-danger-200 rounded-xl flex items-start gap-3 animate-slide-in">
                <AlertCircle className="w-5 h-5 text-danger-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-danger-900">Upload Failed</p>
                  <p className="text-sm text-danger-700 mt-0.5">{uploadError}</p>
                </div>
              </div>
            )}

            {uploadSuccess && (
              <div className="mt-6 p-4 bg-success-50 border border-success-200 rounded-xl flex items-start gap-3 animate-slide-in">
                <CheckCircle2 className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-success-900">Upload Successful!</p>
                  <p className="text-sm text-success-700 mt-0.5">Invoice extracted. Review the details below.</p>
                </div>
              </div>
            )}

            {/* Global Support Info */}
            <div className="mt-8 grid md:grid-cols-3 gap-4">
              <div className="p-6 bg-white rounded-xl shadow-soft border border-secondary-100">
                <div className="text-2xl mb-2">🇮🇳</div>
                <h3 className="font-semibold text-secondary-900 mb-1">India</h3>
                <p className="text-sm text-secondary-600">GST invoices with GSTIN & PAN</p>
              </div>
              <div className="p-6 bg-white rounded-xl shadow-soft border border-secondary-100">
                <div className="text-2xl mb-2">🇺🇸 🇪🇺</div>
                <h3 className="font-semibold text-secondary-900 mb-1">US & Europe</h3>
                <p className="text-sm text-secondary-600">Sales Tax & VAT invoices</p>
              </div>
              <div className="p-6 bg-white rounded-xl shadow-soft border border-secondary-100">
                <div className="text-2xl mb-2">🌍</div>
                <h3 className="font-semibold text-secondary-900 mb-1">Global</h3>
                <p className="text-sm text-secondary-600">Multiple currencies supported</p>
              </div>
            </div>
          </div>
        ) : (
          // Invoice Review Form
          <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-secondary-900">Review Invoice</h2>
                <p className="text-sm text-secondary-600 mt-1">
                  Invoice ID: {invoice.id?.substring(0, 8)}... • Extracted with AI
                </p>
              </div>
              <button
                onClick={() => {
                  setInvoice(null)
                  setFormData(null)
                  setEditMode(false)
                }}
                className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-xl transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-white rounded-2xl shadow-soft border border-secondary-100 p-8">
              {formData && (
                <form className="space-y-6">
                  {/* Vendor Details */}
                  <div>
                    <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center gap-2">
                      <div className="w-1.5 h-6 bg-primary-600 rounded-full" />
                      Vendor Information
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Vendor Name *
                        </label>
                        <input
                          type="text"
                          value={formData.vendor_name || ''}
                          onChange={(e) => updateField('vendor_name', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                          placeholder="e.g., Acme Corporation"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Invoice Number *
                        </label>
                        <input
                          type="text"
                          value={formData.invoice_number || ''}
                          onChange={(e) => updateField('invoice_number', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                          placeholder="e.g., INV-2024-001"
                        />
                      </div>

                      {/* India-specific fields */}
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          GSTIN (India) <span className="text-secondary-500 text-xs">Optional</span>
                        </label>
                        <input
                          type="text"
                          value={formData.gstin || ''}
                          onChange={(e) => updateField('gstin', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                          placeholder="e.g., 22AAAAA0000A1Z5"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          PAN (India) <span className="text-secondary-500 text-xs">Optional</span>
                        </label>
                        <input
                          type="text"
                          value={formData.pan || ''}
                          onChange={(e) => updateField('pan', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                          placeholder="e.g., AAAAA0000A"
                        />
                      </div>

                      {/* EU VAT field */}
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          VAT Number (EU/UK) <span className="text-secondary-500 text-xs">Optional</span>
                        </label>
                        <input
                          type="text"
                          value={formData.vat_number || ''}
                          onChange={(e) => updateField('vat_number', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                          placeholder="e.g., GB123456789"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Invoice Dates */}
                  <div>
                    <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center gap-2">
                      <div className="w-1.5 h-6 bg-primary-600 rounded-full" />
                      Dates
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Invoice Date *
                        </label>
                        <input
                          type="date"
                          value={formData.invoice_date || ''}
                          onChange={(e) => updateField('invoice_date', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Due Date
                        </label>
                        <input
                          type="date"
                          value={formData.due_date || ''}
                          onChange={(e) => updateField('due_date', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Line Items */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-secondary-900 flex items-center gap-2">
                        <div className="w-1.5 h-6 bg-primary-600 rounded-full" />
                        Line Items
                      </h3>
                      <button
                        type="button"
                        onClick={addLineItem}
                        className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-xl transition-all flex items-center gap-2 shadow-soft hover:shadow-medium"
                      >
                        <Plus className="w-4 h-4" />
                        Add Item
                      </button>
                    </div>

                    <div className="space-y-3">
                      {(formData.line_items || []).map((item, index) => (
                        <div key={index} className="p-4 bg-secondary-50 rounded-xl border border-secondary-200">
                          <div className="grid md:grid-cols-5 gap-3">
                            <div className="md:col-span-2">
                              <label className="block text-xs font-medium text-secondary-700 mb-1">Description</label>
                              <input
                                type="text"
                                value={item.description}
                                onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                                className="w-full px-3 py-2 border border-secondary-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                placeholder="Item description"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-medium text-secondary-700 mb-1">Qty</label>
                              <input
                                type="number"
                                value={item.quantity}
                                onChange={(e) => updateLineItem(index, 'quantity', parseFloat(e.target.value))}
                                className="w-full px-3 py-2 border border-secondary-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                min="0"
                                step="0.01"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-medium text-secondary-700 mb-1">Rate</label>
                              <input
                                type="number"
                                value={item.rate}
                                onChange={(e) => updateLineItem(index, 'rate', parseFloat(e.target.value))}
                                className="w-full px-3 py-2 border border-secondary-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                min="0"
                                step="0.01"
                              />
                            </div>
                            <div className="flex items-end gap-2">
                              <div className="flex-1">
                                <label className="block text-xs font-medium text-secondary-700 mb-1">Amount</label>
                                <input
                                  type="number"
                                  value={item.amount.toFixed(2)}
                                  readOnly
                                  className="w-full px-3 py-2 bg-secondary-100 border border-secondary-300 rounded-lg text-sm text-secondary-700"
                                />
                              </div>
                              <button
                                type="button"
                                onClick={() => removeLineItem(index)}
                                className="p-2 text-danger-600 hover:bg-danger-50 rounded-lg transition-all"
                                title="Remove item"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Amounts */}
                  <div>
                    <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center gap-2">
                      <div className="w-1.5 h-6 bg-primary-600 rounded-full" />
                      Amounts
                    </h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Currency *
                        </label>
                        <select
                          value={formData.currency || 'USD'}
                          onChange={(e) => updateField('currency', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                        >
                          {CURRENCIES.map(curr => (
                            <option key={curr.code} value={curr.code}>
                              {curr.symbol} {curr.code} - {curr.name}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Subtotal *
                        </label>
                        <input
                          type="number"
                          value={formData.subtotal || 0}
                          onChange={(e) => updateField('subtotal', parseFloat(e.target.value))}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                          min="0"
                          step="0.01"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Tax Type
                        </label>
                        <select
                          value={formData.tax_type || 'None'}
                          onChange={(e) => updateField('tax_type', e.target.value)}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                        >
                          {TAX_TYPES.map(tax => (
                            <option key={tax.value} value={tax.value}>
                              {tax.label} ({tax.region})
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Tax Amount
                        </label>
                        <input
                          type="number"
                          value={formData.tax_amount || 0}
                          onChange={(e) => updateField('tax_amount', parseFloat(e.target.value))}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                          min="0"
                          step="0.01"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Tax % <span className="text-secondary-500 text-xs">Optional</span>
                        </label>
                        <input
                          type="number"
                          value={formData.tax_percentage || 0}
                          onChange={(e) => updateField('tax_percentage', parseFloat(e.target.value))}
                          className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                          min="0"
                          max="100"
                          step="0.01"
                          placeholder="e.g., 18 for 18% GST"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-2">
                          Total Amount *
                        </label>
                        <input
                          type="number"
                          value={formData.total_amount || 0}
                          readOnly
                          className="w-full px-4 py-3 bg-primary-50 border border-primary-200 rounded-xl text-primary-900 font-semibold"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Notes */}
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Notes <span className="text-secondary-500 text-xs">Optional</span>
                    </label>
                    <textarea
                      value={formData.notes || ''}
                      onChange={(e) => updateField('notes', e.target.value)}
                      rows={3}
                      className="w-full px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all resize-none"
                      placeholder="Add any additional notes here..."
                    />
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-wrap gap-3 pt-4 border-t border-secondary-200">
                    <button
                      type="button"
                      onClick={handleSave}
                      disabled={saving}
                      className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl
                               focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                               disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-soft hover:shadow-medium
                               flex items-center gap-2"
                    >
                      {saving ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="w-5 h-5" />
                          Save Changes
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={handleExport}
                      disabled={exporting}
                      className="px-6 py-3 bg-success-600 hover:bg-success-700 text-white font-medium rounded-xl
                               transition-all shadow-soft hover:shadow-medium flex items-center gap-2"
                    >
                      {exporting ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Exporting...
                        </>
                      ) : (
                        <>
                          <Download className="w-5 h-5" />
                          Export to QuickBooks
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={handleDelete}
                      className="px-6 py-3 bg-danger-600 hover:bg-danger-700 text-white font-medium rounded-xl
                               transition-all shadow-soft hover:shadow-medium flex items-center gap-2"
                    >
                      <Trash2 className="w-5 h-5" />
                      Delete Invoice
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}
