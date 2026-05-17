/**
 * Lazy loading utilities для оптимизации bundle
 *
 * Components that do not yet exist are provided as stub placeholders
 * to keep TypeScript happy. Replace the dynamic import with the real
 * path once the component is created.
 */

import dynamic from 'next/dynamic'

/* ------------------------------------------------------------------ */
/*  Real components (files exist)                                     */
/* ------------------------------------------------------------------ */

export const LazyChatWidget = dynamic(
  () => import('@/components/ChatWidget'),
  { loading: () => <div className="fixed bottom-4 right-4 w-80 h-96 bg-white rounded-lg shadow-lg flex items-center justify-center"><div className="animate-pulse text-gray-500">Загрузка чата...</div></div>, ssr: false }
)

export const LazyMonitoringDashboard = dynamic(
  () => import('@/components/MonitoringDashboard'),
  { loading: () => <div className="space-y-4">{[...Array(3)].map((_, i) => (<div key={i} className="h-32 bg-gray-200 rounded animate-pulse" />))}</div> }
)

export const LazyStatistics = dynamic(
  () => import('@/components/Statistics'),
  { loading: () => <div className="grid grid-cols-1 md:grid-cols-3 gap-4">{[...Array(3)].map((_, i) => (<div key={i} className="h-24 bg-gray-200 rounded animate-pulse" />))}</div> }
)

export const LazyQuestionDatabase = dynamic(
  () => import('@/components/QuestionDatabase'),
  { loading: () => <div className="space-y-3">{[...Array(5)].map((_, i) => (<div key={i} className="h-16 bg-gray-200 rounded animate-pulse" />))}</div> }
)

export const LazyInterviewTrainer = dynamic(
  () => import('@/components/InterviewTrainer'),
  { loading: () => <div className="p-8 text-center text-gray-500 animate-pulse">Загрузка тренажёра...</div>, ssr: false }
)

export const LazyCodingTasks = dynamic(
  () => import('@/components/CodingTasks'),
  { loading: () => <div className="space-y-4">{[...Array(3)].map((_, i) => (<div key={i} className="h-40 bg-gray-200 rounded animate-pulse" />))}</div> }
)

export const LazyProgressTracker = dynamic(
  () => import('@/components/ProgressTracker'),
  { loading: () => <div className="h-64 bg-gray-200 rounded animate-pulse" /> }
)

export const LazyNotificationsPanel = dynamic(
  () => import('@/components/NotificationsPanel'),
  { loading: () => <div className="space-y-2">{[...Array(5)].map((_, i) => (<div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />))}</div> }
)

/* ------------------------------------------------------------------ */
/*  Stub components (files do not exist yet)                          */
/* ------------------------------------------------------------------ */

const StubPlaceholder = ({ name }: { name: string }) => (
  <div className="p-8 text-center text-gray-500 animate-pulse border-2 border-dashed border-gray-300 rounded-lg">
    <p className="font-semibold">{name}</p>
    <p className="text-sm mt-1">Компонент в разработке</p>
  </div>
)

export const LazyAdminDashboard = () => <StubPlaceholder name="AdminDashboard" />
export const LazyCalendar = () => <StubPlaceholder name="Calendar" />
export const LazyRichTextEditor = () => <StubPlaceholder name="RichTextEditor" />
export const LazyVideoPlayer = () => <StubPlaceholder name="VideoPlayer" />
export const LazyAnalytics = () => <StubPlaceholder name="Analytics" />
export const LazySearchResults = () => <StubPlaceholder name="SearchResults" />
export const LazyCoursePlayer = () => <StubPlaceholder name="CoursePlayer" />
export const LazyPaymentForm = () => <StubPlaceholder name="PaymentForm" />
