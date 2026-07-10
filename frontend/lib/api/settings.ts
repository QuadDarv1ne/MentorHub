/**
 * Settings API — user preferences (language, timezone, notifications, etc.).
 */

import { apiRequest } from './client'

export interface SettingsData {
  language: string
  timezone: string
  emailNotifications: boolean
  pushNotifications: boolean
  profileVisibility: string
  showOnlineStatus: boolean
  showLastSeen: boolean
  twoFactorEnabled: boolean
  sessionsLimit: number
}

export async function getSettings(): Promise<SettingsData> {
  return apiRequest<SettingsData>('/settings')
}

export async function updateSettings(settings: SettingsData): Promise<void> {
  await apiRequest<void>('/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  })
}
