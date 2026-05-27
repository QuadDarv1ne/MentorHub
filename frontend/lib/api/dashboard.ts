/**
 * Dashboard API.
 */

import { apiRequest } from './client'

export interface CourseStats {
  total: number
  in_progress: number
  completed: number
}

export interface SessionStats {
  total: number
  upcoming: number
  completed: number
}

export interface UpcomingSession {
  id: number
  mentor_id: number
  scheduled_at: string | null
  duration_minutes: number | null
  status: string
  meeting_link: string | null
}

export interface RecentActivity {
  type: string
  title: string
  detail: string
  created_at: string | null
}

export interface DashboardData {
  courses: CourseStats
  sessions: SessionStats
  upcoming_sessions: UpcomingSession[]
  recent_activities: RecentActivity[]
}

/** Get dashboard data */
export async function getDashboardData(): Promise<DashboardData> {
  return apiRequest<DashboardData>('/dashboard')
}

/** Get user stats */
export async function getUserStats(): Promise<Record<string, unknown>> {
  return apiRequest<Record<string, unknown>>('/users/me/stats')
}
