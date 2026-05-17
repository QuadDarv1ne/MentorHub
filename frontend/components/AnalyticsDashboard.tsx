'use client'

export default function AnalyticsDashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-6">Analytics Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Platform Overview</h2>
          <p className="text-gray-600 dark:text-gray-400">Analytics dashboard is loading data...</p>
        </div>
      </div>
    </div>
  )
}
