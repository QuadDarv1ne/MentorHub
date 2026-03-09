import { api } from './client'

export interface SimilarCourse {
  course_id: number
  average_rating: number
  total_reviews: number
}

export async function getSimilarCourses(courseId: number): Promise<SimilarCourse[]> {
  try {
    const response = await api.get(`/api/v1/courses/${courseId}/similar`)
    return response.data
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

export async function getMyCourses(): Promise<Course[]> {
  try {
    const response = await api.get('/api/v1/courses/my')
    return response.data
  } catch {
    return []
  }
}

export async function getCourse(id: number): Promise<Course> {
  try {
    const response = await api.get(`/api/v1/courses/${id}`)
    return response.data
  } catch {
    return { id, title: '', description: '', progress: 0 }
  }
}
