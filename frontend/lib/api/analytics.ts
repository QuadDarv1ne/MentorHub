/**
 * Analytics API client.
 */

import { apiRequest } from './client'

export interface UserEngagement {
  user_id: number
  username: string
  sessions_attended: number
  courses_enrolled: number
  avg_progress: number
  reviews_written: number
  last_activity: string | null
  engagement_score: number
}

/** Get current user's engagement stats */
export async function getMyEngagement(): Promise<UserEngagement> {
  return apiRequest<UserEngagement>('/analytics/me/engagement')
}

/** Get engagement stats for a specific user (self or admin only) */
export async function getUserEngagement(userId: number): Promise<UserEngagement> {
  return apiRequest<UserEngagement>(`/analytics/user/${userId}/engagement`)
}

/** User growth data point */
export interface UserGrowthPoint {
  date: string
  new_users: number
}

/** Get user growth data */
export async function getUserGrowth(days = 30): Promise<{ period_days: number; data: UserGrowthPoint[] }> {
  return apiRequest(`/analytics/user-growth?days=${days}`)
}

/** Session analytics breakdown */
export interface SessionAnalytics {
  total: number
  by_status: Record<string, number>
  avg_duration_minutes: number
  top_mentors: Array<{ mentor_id: number; sessions: number }>
}

/** Get session analytics */
export async function getSessionAnalytics(days = 30): Promise<{ period_days: number; analytics: SessionAnalytics }> {
  return apiRequest(`/analytics/sessions?days=${days}`)
}

/** Revenue data point */
export interface RevenuePoint {
  date: string
  revenue: number
}

/** Revenue analytics response */
export interface RevenueAnalytics {
  total_revenue: number
  transaction_count: number
  avg_transaction: number
  daily_revenue: RevenuePoint[]
}

/** Get revenue analytics */
export async function getRevenueAnalytics(days = 30): Promise<{ period_days: number; analytics: RevenueAnalytics }> {
  return apiRequest(`/analytics/revenue?days=${days}`)
}

/** Course performance data */
export interface CoursePerformance {
  course_id: number
  course_title: string
  enrollments: number
  avg_progress: number
  completed: number
  completion_rate: number
  avg_rating: number
}

/** Get course analytics (all courses or specific one) */
export async function getCourseAnalytics(courseId?: number): Promise<CoursePerformance | { courses: CoursePerformance[] }> {
  const qs = courseId ? `?course_id=${courseId}` : ''
  return apiRequest(`/analytics/courses${qs}`)
}
