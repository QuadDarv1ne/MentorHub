import dynamic from 'next/dynamic'

const RealTimeDashboard = dynamic(
  () => import('@/components/RealTimeDashboard'),
  { 
    loading: () => (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка dashboard...</p>
        </div>
      </div>
    )
  }
)

export default function DashboardPage() {
  return <RealTimeDashboard />
}
