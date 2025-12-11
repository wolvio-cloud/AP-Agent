'use client'

interface ProcessingTierBadgeProps {
  tier: string
}

export default function ProcessingTierBadge({ tier }: ProcessingTierBadgeProps) {
  const tierConfig: Record<string, { label: string; color: string; bgColor: string }> = {
    uploaded: { label: 'Not Processed', color: 'text-gray-600', bgColor: 'bg-gray-50' },
    tier1: { label: 'Tier 1: Gemini Flash', color: 'text-blue-600', bgColor: 'bg-blue-50' },
    tier2: { label: 'Tier 2: Preprocessed', color: 'text-purple-600', bgColor: 'bg-purple-50' },
    tier3: { label: 'Tier 3: GPT-4V', color: 'text-indigo-600', bgColor: 'bg-indigo-50' },
    tier4: { label: 'Tier 4: Human Review', color: 'text-orange-600', bgColor: 'bg-orange-50' },
    completed: { label: 'Completed', color: 'text-green-600', bgColor: 'bg-green-50' },
  }

  const config = tierConfig[tier] || tierConfig.uploaded

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg ${config.bgColor} border border-opacity-20`}>
      <div className={`w-2 h-2 rounded-full ${config.color.replace('text', 'bg')}`} />
      <span className={`text-sm font-medium ${config.color}`}>{config.label}</span>
    </div>
  )
}
