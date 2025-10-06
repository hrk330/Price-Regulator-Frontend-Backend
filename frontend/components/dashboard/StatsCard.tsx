import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatsCardProps {
  title: string
  value: number | string
  icon: LucideIcon
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
  change?: {
    value: number
    type: 'increase' | 'decrease'
  }
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-50',
    icon: 'text-blue-600',
    text: 'text-blue-600',
  },
  green: {
    bg: 'bg-green-50',
    icon: 'text-green-600',
    text: 'text-green-600',
  },
  yellow: {
    bg: 'bg-yellow-50',
    icon: 'text-yellow-600',
    text: 'text-yellow-600',
  },
  red: {
    bg: 'bg-red-50',
    icon: 'text-red-600',
    text: 'text-red-600',
  },
  purple: {
    bg: 'bg-purple-50',
    icon: 'text-purple-600',
    text: 'text-purple-600',
  },
}

export function StatsCard({ title, value, icon: Icon, color, change }: StatsCardProps) {
  const colors = colorClasses[color]

  return (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center">
          <div className={cn('p-3 rounded-lg', colors.bg)}>
            <Icon className={cn('h-6 w-6', colors.icon)} />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-semibold text-gray-900">{value}</p>
            {change && (
              <p className={cn('text-sm', colors.text)}>
                {change.type === 'increase' ? '+' : '-'}{change.value}%
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
