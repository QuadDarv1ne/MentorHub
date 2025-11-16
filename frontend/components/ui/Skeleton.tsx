'use client'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
}

export default function Skeleton({
  className = '',
  variant = 'rectangular',
  width,
  height
}: SkeletonProps) {
  const variantStyles = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg'
  }

  return (
    <div
      className={`
        animate-pulse bg-gray-200
        ${variantStyles[variant]}
        ${className}
      `}
      {...(width && { style: { width: typeof width === 'number' ? `${width}px` : width } })}
      {...(height && { style: { height: typeof height === 'number' ? `${height}px` : height } })}
    />
  )
}

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center mb-4">
        <Skeleton variant="circular" width={64} height={64} className="mr-4" />
        <div className="flex-1">
          <Skeleton width="60%" height={20} className="mb-2" />
          <Skeleton width="40%" height={16} />
        </div>
      </div>
      <Skeleton width="100%" height={80} className="mb-4" />
      <div className="flex gap-2">
        <Skeleton width={60} height={24} />
        <Skeleton width={80} height={24} />
        <Skeleton width={70} height={24} />
      </div>
    </div>
  )
}
