/**
 * Profile API — user profile data and updates.
 */

import { apiRequest } from './client'

export interface UserProfile {
  id: number
  username: string
  email: string
  fullName: string
  avatar?: string
  role: 'student' | 'mentor' | 'admin'
  bio?: string
  skills: string[]
  rating: number
  totalSessions: number
  completedSessions: number
  joinDate: string
  isOnline: boolean
  lastSeen?: string
}

export async function getProfile(): Promise<UserProfile> {
  return apiRequest<UserProfile>('/users/me/profile')
}

export async function updateProfile(data: {
  full_name?: string
  bio?: string
  skills?: string[]
}): Promise<void> {
  await apiRequest<void>('/users/me/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}
