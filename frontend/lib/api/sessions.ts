/**
 * Sessions API.
 */

import { apiRequest } from './client'

export interface Session {
  id: number
  mentor_id: number
  student_id: number
  mentor_name?: string
  student_name?: string
  topic: string
  scheduled_time: string
  duration: number
  price: number
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled'
  meeting_link?: string
  notes?: string
  created_at?: string
  updated_at?: string
  mentor?: { full_name?: string }
  student?: { full_name?: string }
}

export interface CreateSessionRequest {
  mentor_id: number
  topic: string
  scheduled_time: string
  duration: number
  notes?: string
}

export interface UpdateSessionRequest {
  topic?: string
  scheduled_time?: string
  duration?: number
  status?: Session['status']
  notes?: string
}

/** Get all sessions of the current user */
export async function getMySessions(status?: 'upcoming' | 'past'): Promise<Session[]> {
  const params = status ? `?status=${status}` : ''
  return apiRequest<Session[]>(`/sessions/my${params}`)
}

/** Get a single session by ID */
export async function getSession(id: number): Promise<Session> {
  return apiRequest<Session>(`/sessions/${id}`)
}

/** Create a new session */
export async function createSession(data: CreateSessionRequest): Promise<Session> {
  return apiRequest<Session>('/sessions', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/** Update a session */
export async function updateSession(id: number, data: UpdateSessionRequest): Promise<Session> {
  return apiRequest<Session>(`/sessions/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

/** Cancel a session */
export async function cancelSession(id: number): Promise<Session> {
  return updateSession(id, { status: 'cancelled' })
}

/** Confirm a session */
export async function confirmSession(id: number): Promise<Session> {
  return updateSession(id, { status: 'confirmed' })
}
