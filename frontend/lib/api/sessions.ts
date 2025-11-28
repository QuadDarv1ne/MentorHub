const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface Session {
  id: number;
  mentor_id: number;
  student_id: number;
  mentor_name?: string;
  student_name?: string;
  topic: string;
  scheduled_time: string;
  duration: number;
  price: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  meeting_link?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
  mentor?: {
    full_name?: string;
  };
  student?: {
    full_name?: string;
  };
}

export interface CreateSessionRequest {
  mentor_id: number;
  topic: string;
  scheduled_time: string;
  duration: number;
  notes?: string;
}

export interface UpdateSessionRequest {
  topic?: string;
  scheduled_time?: string;
  duration?: number;
  status?: Session['status'];
  notes?: string;
}

/**
 * Получить все сессии текущего пользователя
 */
export async function getMySessions(status?: 'upcoming' | 'past'): Promise<Session[]> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const params = new URLSearchParams();
  if (status) params.append('status', status);

  const url = `${API_BASE_URL}/sessions/my?${params.toString()}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch sessions: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить сессию по ID
 */
export async function getSession(id: number): Promise<Session> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/sessions/${id}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch session: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Создать новую сессию
 */
export async function createSession(data: CreateSessionRequest): Promise<Session> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/sessions`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create session: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Обновить сессию
 */
export async function updateSession(id: number, data: UpdateSessionRequest): Promise<Session> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/sessions/${id}`;
  
  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to update session: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Отменить сессию
 */
export async function cancelSession(id: number): Promise<Session> {
  return updateSession(id, { status: 'cancelled' });
}

/**
 * Подтвердить сессию
 */
export async function confirmSession(id: number): Promise<Session> {
  return updateSession(id, { status: 'confirmed' });
}
