/**
 * Компоненты для загрузки при динамическом импорте
 */

export function LoadingFallback() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-pulse text-gray-500">Загрузка...</div>
    </div>
  )
}

export function MinimalLoadingFallback() {
  return (
    <div className="flex items-center justify-center p-4">
      <div className="animate-spin">
        <div className="h-8 w-8 border-4 border-gray-300 border-t-blue-600 rounded-full" />
      </div>
    </div>
  )
}

export function SkeletonFallback() {
  return (
    <div className="space-y-4">
      <div className="h-12 bg-gray-200 rounded animate-pulse" />
      <div className="h-12 bg-gray-200 rounded animate-pulse" />
      <div className="h-12 bg-gray-200 rounded animate-pulse" />
    </div>
  )
}
