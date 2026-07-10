/**
 * Calendar API — events, integrations (Google/Outlook), iCal export.
 */

import { apiRequest, apiRequestRaw } from './client'

export interface CalendarEvent {
  id: number
  title: string
  description?: string
  start_time: string
  end_time: string
  type: 'session' | 'meeting' | 'personal'
  participants?: { id: number; name: string; email: string }[]
  location?: string
  video_call_url?: string
}

export async function getCalendarEvents(): Promise<CalendarEvent[]> {
  return apiRequest<CalendarEvent[]>('/calendar/events')
}

export async function syncGoogleCalendar(): Promise<void> {
  await apiRequest<void>('/calendar/sync/google', { method: 'POST' })
}

export async function syncOutlookCalendar(): Promise<void> {
  await apiRequest<void>('/calendar/sync/outlook', { method: 'POST' })
}

export async function exportIcal(): Promise<Response> {
  return apiRequestRaw('/calendar/export/ical')
}
