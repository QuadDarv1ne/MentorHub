const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface Course {
  id: number;
  title: string;
  description: string | null;
  category: string | null;
  difficulty: string | null;
  duration_hours: number;
  price: number;
  is_active: boolean;
  rating: number;
  total_reviews: number;
  thumbnail_url: string | null;
  instructor_id: number;
  created_at: string;
  updated_at: string;
  instructor?: {
    id: number;
    user_id: number;
    full_name?: string;
    specialization?: string;
  } | null;
}

export interface Lesson {
  id: number;
  course_id: number;
  title: string;
  description: string | null;
  content: string | null;
  video_url: string | null;
  duration_minutes: number;
  order: number;
  is_preview: boolean;
  created_at: string;
  updated_at: string;
}

export interface CourseEnrollment {
  id: number;
  user_id: number;
  course_id: number;
  progress_percent: number;
  completed: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CourseWithLessons extends Course {
  lessons: Lesson[];
}

export interface CourseWithEnrollment extends Course {
  enrollment: CourseEnrollment | null;
}

/**
 * Получить все курсы
 */
export async function getCourses(skip: number = 0, limit: number = 100): Promise<Course[]> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  
  const url = `${API_BASE_URL}/courses?${params.toString()}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch courses: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить курсы текущего пользователя
 */
export async function getMyCourses(): Promise<CourseWithEnrollment[]> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses/my`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch my courses: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить курс по ID
 */
export async function getCourse(id: number): Promise<CourseWithLessons> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  
  const url = `${API_BASE_URL}/courses/${id}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch course: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Создать курс
 */
export async function createCourse(data: Omit<Course, 'id' | 'created_at' | 'updated_at' | 'rating' | 'total_reviews'>): Promise<Course> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create course: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Обновить курс
 */
export async function updateCourse(id: number, data: Partial<Omit<Course, 'id' | 'created_at' | 'updated_at' | 'rating' | 'total_reviews'>>): Promise<Course> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses/${id}`;
  
  const response = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to update course: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Удалить курс
 */
export async function deleteCourse(id: number): Promise<void> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses/${id}`;
  
  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete course: ${response.statusText}`);
  }
}

/**
 * Записаться на курс
 */
export async function enrollInCourse(courseId: number): Promise<CourseEnrollment> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses/${courseId}/enroll`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to enroll in course: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить уроки курса
 */
export async function getCourseLessons(courseId: number): Promise<Lesson[]> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  
  const url = `${API_BASE_URL}/courses/${courseId}/lessons`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch course lessons: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Создать урок
 */
export async function createLesson(courseId: number, data: Omit<Lesson, 'id' | 'created_at' | 'updated_at'>): Promise<Lesson> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses/${courseId}/lessons`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create lesson: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Обновить урок
 */
export async function updateLesson(lessonId: number, data: Partial<Omit<Lesson, 'id' | 'created_at' | 'updated_at'>>): Promise<Lesson> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses/lessons/${lessonId}`;
  
  const response = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to update lesson: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Удалить урок
 */
export async function deleteLesson(lessonId: number): Promise<void> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses/lessons/${lessonId}`;
  
  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete lesson: ${response.statusText}`);
  }
}