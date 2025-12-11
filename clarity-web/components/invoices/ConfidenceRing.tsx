'use client'

interface ConfidenceRingProps {
  confidence: number // 0.0 to 1.0
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  label?: string
}

export default function ConfidenceRing({
  confidence,
  size = 'md',
  showLabel = true,
  label
}: ConfidenceRingProps) {
  const percentage = Math.round(confidence * 100)

  // Determine color based on confidence level
  const getColor = () => {
    if (confidence >= 0.95) return 'text-green-600'
    if (confidence >= 0.85) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getBgColor = () => {
    if (confidence >= 0.95) return 'bg-green-100'
    if (confidence >= 0.85) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  const getRingColor = () => {
    if (confidence >= 0.95) return 'stroke-green-600'
    if (confidence >= 0.85) return 'stroke-yellow-600'
    return 'stroke-red-600'
  }

  // Size configurations
  const sizes = {
    sm: { dimension: 40, strokeWidth: 4, fontSize: 'text-xs', padding: 'p-1' },
    md: { dimension: 60, strokeWidth: 5, fontSize: 'text-sm', padding: 'p-2' },
    lg: { dimension: 80, strokeWidth: 6, fontSize: 'text-base', padding: 'p-3' },
  }

  const config = sizes[size]
  const radius = (config.dimension - config.strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (confidence * circumference)

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative inline-flex items-center justify-center">
        <svg
          width={config.dimension}
          height={config.dimension}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={config.dimension / 2}
            cy={config.dimension / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={config.strokeWidth}
            fill="none"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx={config.dimension / 2}
            cy={config.dimension / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={config.strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className={`${getRingColor()} transition-all duration-500 ease-out`}
          />
        </svg>
        {/* Percentage text */}
        <div className={`absolute inset-0 flex items-center justify-center ${config.fontSize} font-bold ${getColor()}`}>
          {percentage}%
        </div>
      </div>
      {showLabel && label && (
        <span className="text-xs text-gray-600 font-medium">{label}</span>
      )}
    </div>
  )
}
