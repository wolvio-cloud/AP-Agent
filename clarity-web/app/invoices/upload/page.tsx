'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import UploadZone from '@/components/invoices/UploadZone'
import { ArrowLeft, CheckCircle2 } from 'lucide-react'
import Link from 'next/link'

function UploadPageContent() {
  const router = useRouter()
  const [uploadedCount, setUploadedCount] = useState(0)
  const [uploadedIds, setUploadedIds] = useState<string[]>([])

  const handleUploadComplete = (fileId: string, fileName: string) => {
    setUploadedCount(prev => prev + 1)
    setUploadedIds(prev => [...prev, fileId])
  }

  const handleUploadError = (fileName: string, error: string) => {
    console.error(`Upload failed for ${fileName}:`, error)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Upload Invoices</h1>
              <p className="text-sm text-gray-600 mt-1">
                Upload your invoices for AI-powered processing
              </p>
            </div>
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition"
            >
              <ArrowLeft size={20} />
              Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto p-8">
        {/* Success Message */}
        {uploadedCount > 0 && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
            <CheckCircle2 className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
            <div className="flex-1">
              <h3 className="font-medium text-green-900">
                {uploadedCount} {uploadedCount === 1 ? 'invoice' : 'invoices'} uploaded successfully!
              </h3>
              <p className="text-sm text-green-700 mt-1">
                Your invoices are ready for processing. You can upload more or view them in the invoices list.
              </p>
            </div>
          </div>
        )}

        {/* Upload Zone */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          <UploadZone
            onUploadComplete={handleUploadComplete}
            onUploadError={handleUploadError}
          />
        </div>

        {/* Action Buttons */}
        {uploadedCount > 0 && (
          <div className="mt-6 flex gap-4 justify-center">
            <button
              onClick={() => router.push('/invoices')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
            >
              View All Invoices
            </button>
            <button
              onClick={() => {
                if (uploadedIds.length > 0) {
                  router.push(`/invoices/${uploadedIds[uploadedIds.length - 1]}`)
                }
              }}
              className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition font-medium"
            >
              View Latest Upload
            </button>
          </div>
        )}

        {/* Info Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 p-6 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">What happens next?</h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <span className="font-medium">1.</span>
              <span>Your invoices are securely stored in cloud storage</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-medium">2.</span>
              <span>AI will extract data from your invoices (coming in Phase 4)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-medium">3.</span>
              <span>Extracted data will be validated for accuracy (Phase 5)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-medium">4.</span>
              <span>GL codes will be automatically assigned (Phase 5)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-medium">5.</span>
              <span>You can review and approve the processed invoices</span>
            </li>
          </ul>
        </div>
      </main>
    </div>
  )
}

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <UploadPageContent />
    </ProtectedRoute>
  )
}
