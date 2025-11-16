export async function getMyProgress(courseId?: number) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const url = `/api/v1/users/me/progress${courseId ? `?course_id=${courseId}` : ''}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (!res.ok) {
    throw new Error('Failed to fetch progress');
  }

  return res.json();
}

export async function upsertProgress(payload: { course_id: number; lesson_id?: number | null; progress_percent: number; completed?: boolean }) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const res = await fetch(`/api/v1/progress`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to save progress');
  }

  return res.json();
}
