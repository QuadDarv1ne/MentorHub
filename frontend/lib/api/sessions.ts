/**
 * Sessions API.
 */

import { apiRequest } from './client'

export interface Session {
  id: number
  mentor_id: number
  student_id: number
  topic?: string
  scheduled_at: string
  duration_minutes: number
  status: string
  meeting_link?: string
  notes?: string
  created_at?: string
  mentor?: { full_name?: string; avatar_url?: string }
  student?: { full_name?: string; avatar_url?: string }
}

export interface CreateSessionRequest {
  mentor_id: number
  topic?: string
  scheduled_at: string
  duration_minutes: number
  notes?: string
}

export interface UpdateSessionRequest {
  topic?: string
  scheduled_at?: string
  duration_minutes?: number
  status?: string
  notes?: string
}

/** Get all sessions of the current user */
export async function getMySessions(): Promise<Session[]> {
  return apiRequest<Session[]>('/sessions/my')
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

export interface SubmitRatingRequest {
  reviewed_id: number
  rating: number
  comment?: string
  session_id: number
}

/** Submit a review/rating for a mentor after a completed session */
export async function submitSessionRating(data: SubmitRatingRequest): Promise<unknown> {
  return apiRequest('/reviews', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
