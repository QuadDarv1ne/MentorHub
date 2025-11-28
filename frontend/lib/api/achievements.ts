const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface Achievement {
  id: number;
  user_id: number;
  title: string;
  description: string;
  icon: string;
  earned_at: string;
}

/**
 * Получить все достижения текущего пользователя
 */
export async function getMyAchievements(): Promise<Achievement[]> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/achievements/my`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch achievements: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить достижение по ID
 */
export async function getAchievement(id: number): Promise<Achievement> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/achievements/${id}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch achievement: ${response.statusText}`);
  }

  return response.json();
}