const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface Course {
  id: number;
  user_id: number;
  course_id: number;
  rating: number;
  comment?: string;
  created_at?: string;
  updated_at?: string;
  user_name?: string;
}

/**
 * Получить все курсы текущего пользователя
 */
export async function getMyCourses(): Promise<Course[]> {
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
    throw new Error(`Failed to fetch courses: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить курс по ID
 */
export async function getCourse(id: number): Promise<Course> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/courses/${id}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch course: ${response.statusText}`);
  }

  return response.json();
}