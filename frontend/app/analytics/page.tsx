import dynamic from 'next/dynamic'

const AnalyticsDashboard = dynamic(
  () => import('@/components/AnalyticsDashboard'),
  { 
    loading: () => (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка...</p>
        </div>
      </div>
    )
  }
)

export default function AnalyticsPage() {
  return <AnalyticsDashboard />
}
