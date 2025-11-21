/**
 * Loading skeleton компоненты для улучшенного UX
 * Показываются во время загрузки данных
 */

import React from 'react'

// Базовый скелетон
interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  lines?: number
}

export function Skeleton({
  className = '',
  variant = 'text',
  width,
  height,
  lines = 1,
}: SkeletonProps) {
  const variantClass = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  }[variant]

  const widthClass = width ? (typeof width === 'number' ? `w-[${width}px]` : width) : 'w-full'
  const heightClass = height ? (typeof height === 'number' ? `h-[${height}px]` : height) : ''

  if (variant === 'text' && lines > 1) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={`animate-pulse bg-gray-200 ${variantClass} ${i === lines - 1 ? 'w-4/5' : widthClass}`}
            aria-hidden="true"
          />
        ))}
      </div>
    )
  }

  return (
    <div
      className={`animate-pulse bg-gray-200 ${variantClass} ${widthClass} ${heightClass} ${className}`}
      aria-hidden="true"
    />
  )
}

// Скелетон карточки
export function CardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 space-y-4">
      <div className="flex items-center space-x-4">
        <Skeleton variant="circular" width={48} height={48} />
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" />
        </div>
      </div>
      <Skeleton variant="text" lines={3} />
      <div className="flex gap-2">
        <Skeleton variant="rectangular" width={80} height={32} />
        <Skeleton variant="rectangular" width={80} height={32} />
      </div>
    </div>
  )
}

// Скелетон списка
interface ListSkeletonProps {
  count?: number
}

export function ListSkeleton({ count = 3 }: ListSkeletonProps) {
  return (
    <div className="space-y-4" role="status" aria-label="Загрузка списка">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-start space-x-4">
            <Skeleton variant="circular" width={40} height={40} />
            <div className="flex-1 space-y-2">
              <Skeleton variant="text" width="70%" />
              <Skeleton variant="text" width="50%" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

// Скелетон профиля ментора
export function MentorCardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 space-y-4">
      <div className="flex items-start space-x-4">
        <Skeleton variant="circular" width={80} height={80} />
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" width="60%" height={24} />
          <Skeleton variant="text" width="40%" />
          <div className="flex gap-2 mt-2">
            <Skeleton variant="rectangular" width={60} height={20} />
            <Skeleton variant="rectangular" width={60} height={20} />
          </div>
        </div>
      </div>
      <Skeleton variant="text" lines={3} />
      <div className="flex items-center justify-between pt-4 border-t">
        <Skeleton variant="text" width={80} />
        <Skeleton variant="rectangular" width={100} height={36} />
      </div>
    </div>
  )
}

// Скелетон таблицы
interface TableSkeletonProps {
  rows?: number
  columns?: number
}

export function TableSkeleton({ rows = 5, columns = 4 }: TableSkeletonProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {Array.from({ length: columns }).map((_, i) => (
              <th key={i} className="px-6 py-3">
                <Skeleton variant="text" width="80%" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td key={colIndex} className="px-6 py-4">
                  <Skeleton variant="text" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// Скелетон формы
export function FormSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton variant="text" width={100} height={16} />
        <Skeleton variant="rectangular" height={40} />
      </div>
      <div className="space-y-2">
        <Skeleton variant="text" width={120} height={16} />
        <Skeleton variant="rectangular" height={40} />
      </div>
      <div className="space-y-2">
        <Skeleton variant="text" width={80} height={16} />
        <Skeleton variant="rectangular" height={100} />
      </div>
      <Skeleton variant="rectangular" width={120} height={40} />
    </div>
  )
}

// Скелетон статистики/метрик
export function StatsCardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2 flex-1">
          <Skeleton variant="text" width={120} />
          <Skeleton variant="text" width={80} height={32} />
        </div>
        <Skeleton variant="circular" width={48} height={48} />
      </div>
      <div className="mt-4">
        <Skeleton variant="text" width="60%" />
      </div>
    </div>
  )
}

// Скелетон дашборда
export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div>
        <Skeleton variant="text" width={200} height={32} />
        <Skeleton variant="text" width={300} className="mt-2" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatsCardSkeleton key={i} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Skeleton variant="text" width={180} height={24} />
          <ListSkeleton count={3} />
        </div>
        <div className="space-y-4">
          <Skeleton variant="text" width={180} height={24} />
          <CardSkeleton />
        </div>
      </div>
    </div>
  )
}

// Компонент страницы с loading state
interface PageSkeletonProps {
  children?: React.ReactNode
  loading?: boolean
  skeleton?: React.ReactNode
}

export function PageSkeleton({ children, loading = false, skeleton }: PageSkeletonProps) {
  if (loading) {
    return (
      <div className="animate-pulse" role="status" aria-live="polite" aria-label="Загрузка страницы">
        {skeleton || <DashboardSkeleton />}
      </div>
    )
  }

  return <>{children}</>
}
