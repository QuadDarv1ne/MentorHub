/**
 * Утилита для динамического импорта компонентов с поддержкой loading/error states
 * Используется для оптимизации загрузки больших компонентов
 */

import dynamic from 'next/dynamic'
import { LoadingFallback, MinimalLoadingFallback, SkeletonFallback } from '@/components/LoadingFallback'

/**
 * Предустановки для часто используемых компонентов
 */
export const lazyComponents = {
  // Heavy monitoring dashboard
  monitoringDashboard: dynamic(() => import('@/components/MonitoringDashboard'), {
    loading: MinimalLoadingFallback,
    ssr: false,
  }),

  // Interview trainer
  interviewTrainer: dynamic(() => import('@/components/InterviewTrainer'), {
    loading: MinimalLoadingFallback,
    ssr: false,
  }),

  // Coding tasks
  codingTasks: dynamic(() => import('@/components/CodingTasks'), {
    loading: SkeletonFallback,
    ssr: false,
  }),

  // Question database
  questionDatabase: dynamic(() => import('@/components/QuestionDatabase'), {
    loading: SkeletonFallback,
    ssr: false,
  }),

  // Statistics charts
  statistics: dynamic(() => import('@/components/Statistics'), {
    loading: MinimalLoadingFallback,
    ssr: false,
  }),

  // Progress tracking
  progressTracker: dynamic(() => import('@/components/ProgressTracker'), {
    loading: SkeletonFallback,
    ssr: false,
  }),

  // Similar courses recommendations
  similarCourses: dynamic(() => import('@/components/SimilarCourses'), {
    loading: SkeletonFallback,
    ssr: true,
  }),

  // Review form
  reviewForm: dynamic(() => import('@/components/ReviewForm'), {
    loading: MinimalLoadingFallback,
    ssr: false,
  }),

  // Review list
  reviewList: dynamic(() => import('@/components/ReviewList'), {
    loading: SkeletonFallback,
    ssr: true,
  }),

  // Mentors preview
  mentorsPreview: dynamic(() => import('@/components/MentorsPreview'), {
    loading: SkeletonFallback,
    ssr: true,
  }),
}

// Re-export loading components
export { LoadingFallback, MinimalLoadingFallback, SkeletonFallback }

