import { HTMLAttributes, ReactNode } from 'react'

interface StatCardProps extends HTMLAttributes<HTMLDivElement> {
  title: string
  value: string | number
  icon?: ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  description?: string
}

export default function StatCard({
  title,
  value,
  icon,
  trend,
  description,
  className = '',
  ...props
}: StatCardProps) {
  return (
    <div
      className={`bg-white rounded-xl border border-gray-200 p-6 ${className}`}
      {...props}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {description && (
            <p className="text-sm text-gray-500 mt-2">{description}</p>
          )}
          {trend && (
            <div className="flex items-center mt-2">
              <span
                className={`text-sm font-medium ${
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-sm text-gray-500 ml-2">за месяц</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="ml-4 p-3 bg-indigo-50 rounded-lg">
            <div className="text-indigo-600">{icon}</div>
          </div>
        )}
      </div>
    </div>
  )
}
