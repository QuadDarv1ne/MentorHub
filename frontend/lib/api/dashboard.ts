const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface DashboardStats {
  total_courses: number;
  in_progress: number;
  completed: number;
  total_sessions: number;
  upcoming_sessions: number;
  completed_sessions: number;
  total_reviews: number;
  average_rating: number;
}

export interface UpcomingSession {
  id: number;
  mentor_name: string;
  topic: string;
  scheduled_time: string;
  duration: number;
  status: string;
}

export interface RecentActivity {
  id: number;
  type: 'course_started' | 'course_completed' | 'session_completed' | 'review_posted';
  title: string;
  description: string;
  timestamp: string;
  icon_color?: string;
}

export interface DashboardData {
  stats: DashboardStats;
  upcoming_sessions: UpcomingSession[];
  recent_activities: RecentActivity[];
}

/**
 * Получить данные для дашборда
 */
export async function getDashboardData(): Promise<DashboardData> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/dashboard`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить статистику пользователя
 */
export async function getUserStats(): Promise<DashboardStats> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/users/me/stats`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch user stats: ${response.statusText}`);
  }

  return response.json();
}
