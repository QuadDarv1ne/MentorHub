import { apiRequest } from './client'

export interface SimilarCourse {
  course_id: number
  average_rating: number
  total_reviews: number
}

export async function getSimilarCourses(courseId: number): Promise<SimilarCourse[]> {
  try {
    return await apiRequest(`/courses/${courseId}/similar`)
  } catch {
    return []
  }
}

export interface Course {
  id: number
  title: string
  description: string
  progress: number
  certificate?: boolean
}

export async function getCourses(skip?: number, limit?: number): Promise<Course[]> {
  try {
    const params = new URLSearchParams()
    if (skip !== undefined) params.append('skip', skip.toString())
    if (limit !== undefined) params.append('limit', limit.toString())
    
    const queryString = params.toString()
    const url = queryString ? `/courses?${queryString}` : '/courses'
    
    return await apiRequest<Course[]>(url)
  } catch {
    return []
  }
}

export async function getMyCourses(): Promise<Course[]> {
  try {
    return await apiRequest<Course[]>('/courses/my')
  } catch {
    return []
  }
}

export async function getCourse(id: number): Promise<Course> {
  try {
    return await apiRequest<Course>(`/courses/${id}`)
  } catch {
    return { id, title: '', description: '', progress: 0 }
  }
}
