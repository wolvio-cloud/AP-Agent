'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, CheckCircle2, X, Loader2 } from 'lucide-react'

interface UploadedFile {
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
  id?: string
}

interface UploadZoneProps {
  onUploadComplete?: (fileId: string, fileName: string) => void
  onUploadError?: (fileName: string, error: string) => void
}

const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
}

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export default function UploadZone({ onUploadComplete, onUploadError }: UploadZoneProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])

  const uploadFile = async (uploadedFile: UploadedFile) => {
    const formData = new FormData()
    formData.append('file', uploadedFile.file)

    try {
      // Update status to uploading
      setUploadedFiles(prev =>
        prev.map(f =>
          f.file === uploadedFile.file
            ? { ...f, status: 'uploading' as const, progress: 0 }
            : f
        )
      )

      const token = localStorage.getItem('access_token')
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/invoices/upload`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Upload failed')
      }

      const result = await response.json()

      // Update status to success
      setUploadedFiles(prev =>
        prev.map(f =>
          f.file === uploadedFile.file
            ? { ...f, status: 'success' as const, progress: 100, id: result.data.id }
            : f
        )
      )

      if (onUploadComplete) {
        onUploadComplete(result.data.id, uploadedFile.file.name)
      }
    } catch (error: any) {
      // Update status to error
      setUploadedFiles(prev =>
        prev.map(f =>
          f.file === uploadedFile.file
            ? { ...f, status: 'error' as const, error: error.message }
            : f
        )
      )

      if (onUploadError) {
        onUploadError(uploadedFile.file.name, error.message)
      }
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      file,
      status: 'pending',
      progress: 0,
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])

    // Upload files one by one
    newFiles.forEach(uploadFile)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: true,
  })

  const removeFile = (file: File) => {
    setUploadedFiles(prev => prev.filter(f => f.file !== file))
  }

  return (
    <div className="w-full">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center">
          <Upload
            size={48}
            className={`mb-4 ${isDragActive ? 'text-blue-500' : 'text-gray-400'}`}
          />
          <p className="text-lg font-medium mb-2">
            {isDragActive ? 'Drop files here' : 'Drag & drop invoices here'}
          </p>
          <p className="text-sm text-gray-600 mb-4">or click to browse files</p>
          <p className="text-xs text-gray-500">
            Supported formats: PDF, JPG, PNG (Max 10MB)
          </p>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-medium text-gray-700">Uploaded Files</h3>
          {uploadedFiles.map((uploadedFile, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 bg-white border rounded-lg"
            >
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                <div className="flex-shrink-0">
                  {uploadedFile.status === 'pending' && (
                    <File size={20} className="text-gray-400" />
                  )}
                  {uploadedFile.status === 'uploading' && (
                    <Loader2 size={20} className="text-blue-500 animate-spin" />
                  )}
                  {uploadedFile.status === 'success' && (
                    <CheckCircle2 size={20} className="text-green-500" />
                  )}
                  {uploadedFile.status === 'error' && (
                    <X size={20} className="text-red-500" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {uploadedFile.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>

                  {uploadedFile.status === 'uploading' && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div
                          className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${uploadedFile.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {uploadedFile.status === 'error' && uploadedFile.error && (
                    <p className="text-xs text-red-600 mt-1">{uploadedFile.error}</p>
                  )}
                </div>
              </div>

              <button
                onClick={() => removeFile(uploadedFile.file)}
                className="ml-4 p-1 text-gray-400 hover:text-red-600 transition"
                title="Remove"
              >
                <X size={18} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
