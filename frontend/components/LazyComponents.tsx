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

// AdminDashboard - ленивая загрузка (тяжёлый компонент с графиками)
export const LazyAdminDashboard = dynamic(
  () => import('@/components/AdminDashboard'),
  {
   loading: () => (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-24 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    ),
  }
)

// Calendar - ленивая загрузка (большая библиотека)
export const LazyCalendar = dynamic(
  () => import('@/components/Calendar'),
  {
   loading: () => (
      <div className="h-96 bg-gray-100 rounded animate-pulse flex items-center justify-center">
        <span className="text-gray-500">Загрузка календаря...</span>
      </div>
    ),
  }
)

// RichTextEditor - ленивая загрузка (тяжёлый WYSIWYG редактор)
export const LazyRichTextEditor = dynamic(
  () => import('@/components/RichTextEditor'),
  {
   loading: () => (
      <div className="h-64 border rounded animate-pulse bg-gray-50" />
    ),
  }
)

// VideoPlayer - ленивая загрузка
export const LazyVideoPlayer = dynamic(
  () => import('@/components/VideoPlayer'),
  {
   loading: () => (
      <div className="aspect-video bg-black rounded flex items-center justify-center">
        <div className="animate-pulse text-white">Загрузка видео...</div>
      </div>
    ),
   ssr: false,
  }
)

// Analytics - ленивая загрузка (графики и диаграммы)
export const LazyAnalytics = dynamic(
  () => import('@/components/Analytics'),
  {
   loading: () => (
      <div className="grid grid-cols-2 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-48 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    ),
  }
)

// NotificationsPanel - ленивая загрузка
export const LazyNotificationsPanel = dynamic(
  () => import('@/components/NotificationsPanel'),
  {
   loading: () => (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
        ))}
      </div>
    ),
  }
)

// SearchResults - ленивая загрузка
export const LazySearchResults = dynamic(
  () => import('@/components/SearchResults'),
  {
   loading: () => (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-20 bg-gray-100 rounded animate-pulse" />
        ))}
      </div>
    ),
  }
)

// CoursePlayer - ленивая загрузка (видео + материалы)
export const LazyCoursePlayer = dynamic(
  () => import('@/components/CoursePlayer'),
  {
   loading: () => (
      <div className="space-y-4">
        <div className="aspect-video bg-black rounded animate-pulse" />
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      </div>
    ),
   ssr: false,
  }
)

// PaymentForm - ленивая загрузка (Stripe элементы)
export const LazyPaymentForm = dynamic(
  () => import('@/components/PaymentForm'),
  {
   loading: () => (
      <div className="space-y-4 p-6 border rounded">
        <div className="h-10 bg-gray-100 rounded animate-pulse" />
        <div className="h-10 bg-gray-100 rounded animate-pulse" />
        <div className="h-12 bg-gray-200 rounded animate-pulse" />
      </div>
    ),
  }
)
