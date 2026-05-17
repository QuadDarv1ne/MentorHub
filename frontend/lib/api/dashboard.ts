/**
 * Dashboard API.
 */

import { apiRequest } from './client'

export interface DashboardStats {
  total_courses: number
  in_progress: number
  completed: number
  total_sessions: number
  upcoming_sessions: number
  completed_sessions: number
  total_reviews: number
  average_rating: number
}

export interface UpcomingSession {
  id: number
  mentor_name: string
  topic: string
  scheduled_time: string
  duration: number
  status: string
}

export interface RecentActivity {
  id: number
  type: 'course_started' | 'course_completed' | 'session_completed' | 'review_posted'
  title: string
  description: string
  timestamp: string
  icon_color?: string
}

export interface DashboardData {
  stats: DashboardStats
  upcoming_sessions: UpcomingSession[]
  recent_activities: RecentActivity[]
}

/** Get dashboard data */
export async function getDashboardData(): Promise<DashboardData> {
  return apiRequest<DashboardData>('/dashboard')
}

/** Get user stats */
export async function getUserStats(): Promise<DashboardStats> {
  return apiRequest<DashboardStats>('/users/me/stats')
}
