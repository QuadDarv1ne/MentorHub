/**
 * Progress API.
 */

import { apiRequest } from './client'

export async function getMyProgress(courseId?: number) {
  const params = courseId ? `?course_id=${courseId}` : ''
  return apiRequest(`/users/me/progress${params}`)
}

export async function upsertProgress(payload: { course_id: number; lesson_id?: number | null; progress_percent: number; completed?: boolean }) {
  return apiRequest('/progress', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
