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
