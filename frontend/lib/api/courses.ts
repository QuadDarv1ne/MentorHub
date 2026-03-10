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

export interface Instructor {
  id: number
  user_id: number
  full_name?: string
  specialization?: string
}

export interface Course {
  id: number
  title: string
  description: string | null
  category: string | null
  difficulty: string | null
  duration_hours: number
  price: number
  is_active: boolean
  rating: number
  total_reviews: number
  thumbnail_url: string | null
  instructor_id: number
  created_at: string
  updated_at: string
  progress?: number
  certificate?: boolean
  instructor?: Instructor | null
}

export interface CourseWithEnrollment extends Course {
  enrollment?: {
    id: number
    progress_percent: number
    completed: boolean
    completed_at?: string
    created_at: string
    updated_at: string
  } | null
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

export async function getMyCourses(): Promise<CourseWithEnrollment[]> {
  try {
    return await apiRequest<CourseWithEnrollment[]>('/courses/my')
  } catch {
    return []
  }
}

export async function getCourse(id: number): Promise<Course> {
  try {
    return await apiRequest<Course>(`/courses/${id}`)
  } catch {
    return { id, title: '', description: null, category: null, difficulty: null, duration_hours: 0, price: 0, is_active: true, rating: 0, total_reviews: 0, thumbnail_url: null, instructor_id: 0, created_at: '', updated_at: '' }
  }
}
