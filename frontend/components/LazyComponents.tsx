/**
 * Lazy loading utilities для оптимизации bundle
 * Используем Next.js dynamic напрямую для лучшей типизации
 */

import dynamic from 'next/dynamic'

// Chat Widget - ленивая загрузка
export const LazyChatWidget = dynamic(
  () => import('@/components/ChatWidget'),
  {
   loading: () => (
      <div className="fixed bottom-4 right-4 w-80 h-96 bg-white rounded-lg shadow-lg flex items-center justify-center">
        <div className="animate-pulse text-gray-500">Загрузка чата...</div>
      </div>
    ),
   ssr: false, // Чат только на клиенте
  }
)

// Monitoring Dashboard - ленивая загрузка
export const LazyMonitoringDashboard = dynamic(
  () => import('@/components/MonitoringDashboard'),
  {
   loading: () => (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    ),
  }
)

// Statistics - ленивая загрузка
export const LazyStatistics = dynamic(
  () => import('@/components/Statistics'),
  {
   loading: () => (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-24 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    ),
  }
)

// QuestionDatabase - ленивая загрузка
export const LazyQuestionDatabase = dynamic(
  () => import('@/components/QuestionDatabase'),
  {
   loading: () => (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    ),
  }
)

// InterviewTrainer - ленивая загрузка
export const LazyInterviewTrainer = dynamic(
  () => import('@/components/InterviewTrainer'),
  {
   loading: () => (
      <div className="p-8 text-center text-gray-500 animate-pulse">
        Загрузка тренажёра...
      </div>
    ),
   ssr: false,
  }
)

// CodingTasks - ленивая загрузка
export const LazyCodingTasks = dynamic(
  () => import('@/components/CodingTasks'),
  {
   loading: () => (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-40 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    ),
  }
)

// ProgressTracker - ленивая загрузка
export const LazyProgressTracker = dynamic(
  () => import('@/components/ProgressTracker'),
  {
   loading: () => (
      <div className="h-64 bg-gray-200 rounded animate-pulse" />
    ),
  }
)
