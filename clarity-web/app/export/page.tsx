'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import {
  FileText,
  Download,
  Search,
  Filter,
  CheckSquare,
  Square,
  Loader2,
  FileSpreadsheet,
  Package,
  AlertCircle,
  ArrowLeft,
  Eye,
  Trash2,
  CheckCircle2,
  Clock,
  Send,
} from 'lucide-react'

// Invoice interface
interface Invoice {
  id: string
  vendor_name: string
  invoice_number: string
  invoice_date: string
  due_date: string
  total_amount: number
  currency: string
  tax_type: string
  status: 'extracted' | 'reviewed' | 'exported'
  created_at: string
  gstin?: string
  pan?: string
  vat_number?: string
}

// Currency symbols mapping
const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: '$',
  EUR: '€',
  GBP: '£',
  INR: '₹',
  AUD: 'A$',
  CAD: 'C$',
  SGD: 'S$',
  AED: 'د.إ',
}

// Status badge component
function StatusBadge({ status }: { status: Invoice['status'] }) {
  const config = {
    extracted: {
      label: 'Extracted',
      icon: Clock,
      classes: 'bg-warning-50 text-warning-700 border-warning-200',
    },
    reviewed: {
      label: 'Reviewed',
      icon: CheckCircle2,
      classes: 'bg-primary-50 text-primary-700 border-primary-200',
    },
    exported: {
      label: 'Exported',
      icon: Send,
      classes: 'bg-success-50 text-success-700 border-success-200',
    },
  }

  const { label, icon: Icon, classes } = config[status]

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg border text-xs font-medium ${classes}`}>
      <Icon className="w-3.5 h-3.5" />
      {label}
    </span>
  )
}

export default function ExportPage() {
  const router = useRouter()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [filteredInvoices, setFilteredInvoices] = useState<Invoice[]>([])
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | Invoice['status']>('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)
  const [exportingCsv, setExportingCsv] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  // Load invoices on mount
  useEffect(() => {
    loadInvoices()
  }, [])

  // Filter invoices when search or status changes
  useEffect(() => {
    let filtered = invoices

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (inv) =>
          inv.vendor_name.toLowerCase().includes(query) ||
          inv.invoice_number.toLowerCase().includes(query) ||
          inv.currency.toLowerCase().includes(query) ||
          inv.tax_type.toLowerCase().includes(query)
      )
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((inv) => inv.status === statusFilter)
    }

    setFilteredInvoices(filtered)
  }, [searchQuery, statusFilter, invoices])

  const loadInvoices = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getInvoices()
      setInvoices(data)
      setFilteredInvoices(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }

  const toggleSelection = (id: string) => {
    const newSelection = new Set(selectedIds)
    if (newSelection.has(id)) {
      newSelection.delete(id)
    } else {
      newSelection.add(id)
    }
    setSelectedIds(newSelection)
  }

  const selectAll = () => {
    const allIds = new Set(filteredInvoices.map((inv) => inv.id))
    setSelectedIds(allIds)
  }

  const deselectAll = () => {
    setSelectedIds(new Set())
  }

  const formatCurrency = (amount: number, currency: string) => {
    const symbol = CURRENCY_SYMBOLS[currency] || currency
    return `${symbol}${amount.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const handleExportSingle = async (invoiceId: string) => {
    try {
      setExporting(true)
      const blob = await apiClient.exportInvoiceIIF(invoiceId)
      const invoice = invoices.find((inv) => inv.id === invoiceId)
      const filename = `invoice_${invoice?.invoice_number || invoiceId}.iif`

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      // Update invoice status to exported
      await apiClient.updateInvoice(invoiceId, { status: 'exported' })
      await loadInvoices()
    } catch (err: any) {
      alert(err.message || 'Export failed')
    } finally {
      setExporting(false)
    }
  }

  const handleExportBatch = async () => {
    if (selectedIds.size === 0) {
      alert('Please select at least one invoice')
      return
    }

    try {
      setExporting(true)
      const blob = await apiClient.exportInvoicesIIFBatch(Array.from(selectedIds))
      const filename = `invoices_batch_${Date.now()}.iif`

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      // Update all selected invoices to exported
      await Promise.all(
        Array.from(selectedIds).map((id) =>
          apiClient.updateInvoice(id, { status: 'exported' })
        )
      )
      await loadInvoices()
      deselectAll()
    } catch (err: any) {
      alert(err.message || 'Batch export failed')
    } finally {
      setExporting(false)
    }
  }

  const handleExportCSV = async () => {
    try {
      setExportingCsv(true)
      const blob = await apiClient.exportInvoicesCSV()
      const filename = `all_invoices_${Date.now()}.csv`

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err: any) {
      alert(err.message || 'CSV export failed')
    } finally {
      setExportingCsv(false)
    }
  }

  const handleDelete = async (invoiceId: string) => {
    if (!confirm('Are you sure you want to delete this invoice? This action cannot be undone.')) {
      return
    }

    try {
      setDeletingId(invoiceId)
      await apiClient.deleteInvoice(invoiceId)
      await loadInvoices()
      // Remove from selection if selected
      const newSelection = new Set(selectedIds)
      newSelection.delete(invoiceId)
      setSelectedIds(newSelection)
    } catch (err: any) {
      alert(err.message || 'Delete failed')
    } finally {
      setDeletingId(null)
    }
  }

  const handleView = (invoiceId: string) => {
    router.push(`/dashboard?invoice=${invoiceId}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Header */}
      <header className="bg-white border-b border-secondary-200 shadow-soft">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="text-secondary-600 hover:text-secondary-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center shadow-soft">
                  <Package className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-secondary-900">Export Invoices</h1>
                  <p className="text-sm text-secondary-600">
                    Manage and export your invoices to QuickBooks
                  </p>
                </div>
              </div>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium transition-colors shadow-soft"
            >
              Upload New
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls Bar */}
        <div className="bg-white rounded-2xl shadow-soft border border-secondary-100 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
                <input
                  type="text"
                  placeholder="Search by vendor, invoice #, currency..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as any)}
                  className="w-full pl-10 pr-4 py-2.5 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all appearance-none bg-white"
                >
                  <option value="all">All Status</option>
                  <option value="extracted">Extracted</option>
                  <option value="reviewed">Reviewed</option>
                  <option value="exported">Exported</option>
                </select>
              </div>
            </div>

            {/* Selection Controls */}
            <div className="flex gap-2">
              <button
                onClick={selectAll}
                className="flex-1 px-3 py-2.5 border border-secondary-300 rounded-xl hover:bg-secondary-50 transition-colors text-sm font-medium text-secondary-700"
              >
                Select All
              </button>
              <button
                onClick={deselectAll}
                className="flex-1 px-3 py-2.5 border border-secondary-300 rounded-xl hover:bg-secondary-50 transition-colors text-sm font-medium text-secondary-700"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Batch Actions */}
          <div className="mt-4 pt-4 border-t border-secondary-200 flex items-center justify-between">
            <div className="text-sm text-secondary-600">
              {selectedIds.size > 0 ? (
                <span className="font-medium text-primary-600">
                  {selectedIds.size} invoice{selectedIds.size > 1 ? 's' : ''} selected
                </span>
              ) : (
                <span>{filteredInvoices.length} invoice{filteredInvoices.length !== 1 ? 's' : ''} found</span>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleExportCSV}
                disabled={exportingCsv || invoices.length === 0}
                className="px-4 py-2 bg-success-600 hover:bg-success-700 text-white rounded-xl font-medium transition-all shadow-soft hover:shadow-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {exportingCsv ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <FileSpreadsheet className="w-4 h-4" />
                    Export All CSV
                  </>
                )}
              </button>

              <button
                onClick={handleExportBatch}
                disabled={exporting || selectedIds.size === 0}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium transition-all shadow-soft hover:shadow-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {exporting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Export Selected IIF ({selectedIds.size})
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-xl flex items-start gap-3 animate-slide-in">
            <AlertCircle className="w-5 h-5 text-danger-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-danger-900">Error Loading Invoices</p>
              <p className="text-sm text-danger-700 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-2xl shadow-soft border border-secondary-100 p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
            <p className="text-secondary-600">Loading invoices...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredInvoices.length === 0 && (
          <div className="bg-white rounded-2xl shadow-soft border border-secondary-100 p-12 text-center">
            <div className="w-16 h-16 bg-secondary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-secondary-400" />
            </div>
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">
              {searchQuery || statusFilter !== 'all' ? 'No invoices found' : 'No invoices yet'}
            </h3>
            <p className="text-secondary-600 mb-6">
              {searchQuery || statusFilter !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Upload your first invoice to get started'}
            </p>
            {!searchQuery && statusFilter === 'all' && (
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium transition-colors shadow-soft"
              >
                <FileText className="w-4 h-4" />
                Upload Invoice
              </Link>
            )}
          </div>
        )}

        {/* Invoice Table */}
        {!loading && filteredInvoices.length > 0 && (
          <div className="bg-white rounded-2xl shadow-soft border border-secondary-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-secondary-50 border-b border-secondary-200">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <button
                        onClick={() => (selectedIds.size === filteredInvoices.length ? deselectAll() : selectAll())}
                        className="text-secondary-500 hover:text-secondary-700"
                      >
                        {selectedIds.size === filteredInvoices.length && filteredInvoices.length > 0 ? (
                          <CheckSquare className="w-5 h-5" />
                        ) : (
                          <Square className="w-5 h-5" />
                        )}
                      </button>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-600 uppercase tracking-wider">
                      Vendor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-600 uppercase tracking-wider">
                      Invoice #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-600 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-600 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-600 uppercase tracking-wider">
                      Tax
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary-600 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-secondary-600 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-secondary-200">
                  {filteredInvoices.map((invoice) => (
                    <tr
                      key={invoice.id}
                      className={`hover:bg-secondary-50 transition-colors ${
                        selectedIds.has(invoice.id) ? 'bg-primary-50' : ''
                      }`}
                    >
                      <td className="px-6 py-4">
                        <button
                          onClick={() => toggleSelection(invoice.id)}
                          className="text-secondary-500 hover:text-secondary-700"
                        >
                          {selectedIds.has(invoice.id) ? (
                            <CheckSquare className="w-5 h-5 text-primary-600" />
                          ) : (
                            <Square className="w-5 h-5" />
                          )}
                        </button>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-secondary-900">
                          {invoice.vendor_name}
                        </div>
                        <div className="text-xs text-secondary-500 flex items-center gap-2 mt-1">
                          {invoice.gstin && <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded">GSTIN</span>}
                          {invoice.pan && <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded">PAN</span>}
                          {invoice.vat_number && <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">VAT</span>}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-secondary-900">
                        {invoice.invoice_number}
                      </td>
                      <td className="px-6 py-4 text-sm text-secondary-900">
                        {formatDate(invoice.invoice_date)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-semibold text-secondary-900">
                          {formatCurrency(invoice.total_amount, invoice.currency)}
                        </div>
                        <div className="text-xs text-secondary-500">{invoice.currency}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-secondary-100 text-secondary-700 rounded text-xs font-medium">
                          {invoice.tax_type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={invoice.status} />
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleView(invoice.id)}
                            className="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                            title="View & Edit"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleExportSingle(invoice.id)}
                            disabled={exporting}
                            className="p-2 text-secondary-600 hover:text-success-600 hover:bg-success-50 rounded-lg transition-colors disabled:opacity-50"
                            title="Export IIF"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(invoice.id)}
                            disabled={deletingId === invoice.id}
                            className="p-2 text-secondary-600 hover:text-danger-600 hover:bg-danger-50 rounded-lg transition-colors disabled:opacity-50"
                            title="Delete"
                          >
                            {deletingId === invoice.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
