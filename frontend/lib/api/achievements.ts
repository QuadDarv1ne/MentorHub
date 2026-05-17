/**
 * Achievements API.
 */

import { apiRequest } from './client'

export interface Achievement {
  id: number
  user_id: number
  title: string
  description: string
  icon: string
  earned_at: string
}

/** Get all achievements for the current user */
export async function getMyAchievements(): Promise<Achievement[]> {
  return apiRequest<Achievement[]>('/achievements/my')
}

/** Get a single achievement by ID */
export async function getAchievement(id: number): Promise<Achievement> {
  return apiRequest<Achievement>(`/achievements/${id}`)
}
