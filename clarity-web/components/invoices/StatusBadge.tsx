'use client'

interface StatusBadgeProps {
  status: string
  size?: 'sm' | 'md'
}

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const statusConfig: Record<string, { color: string; label: string; bgColor: string }> = {
    uploaded: { color: 'text-gray-700', bgColor: 'bg-gray-100', label: 'Uploaded' },
    processing: { color: 'text-blue-700', bgColor: 'bg-blue-100', label: 'Processing' },
    extracted: { color: 'text-green-700', bgColor: 'bg-green-100', label: 'Extracted' },
    requires_review: { color: 'text-yellow-700', bgColor: 'bg-yellow-100', label: 'Needs Review' },
    approved: { color: 'text-green-700', bgColor: 'bg-green-100', label: 'Approved' },
    rejected: { color: 'text-red-700', bgColor: 'bg-red-100', label: 'Rejected' },
    error: { color: 'text-red-700', bgColor: 'bg-red-100', label: 'Error' },
  }

  const config = statusConfig[status] || statusConfig.uploaded
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1'

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${config.color} ${config.bgColor} ${sizeClass}`}>
      {config.label}
    </span>
  )
}
