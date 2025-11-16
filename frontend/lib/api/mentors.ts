const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface Mentor {
  id: number;
  full_name: string;
  email: string;
  bio?: string;
  location?: string;
  occupation?: string;
  hourly_rate?: number;
  experience_years?: number;
  specializations?: string[];
  rating?: number;
  total_sessions?: number;
  avatar_url?: string;
}

export interface MentorsFilters {
  search?: string;
  specialization?: string;
  experience?: string;
  priceRange?: string;
  page?: number;
  limit?: number;
}

export interface MentorsResponse {
  mentors: Mentor[];
  total: number;
  page: number;
  pages: number;
}

/**
 * Получить список менторов с фильтрами
 */
export async function getMentors(filters?: MentorsFilters): Promise<MentorsResponse> {
  const params = new URLSearchParams();
  
  if (filters?.search) params.append('search', filters.search);
  if (filters?.specialization) params.append('specialization', filters.specialization);
  if (filters?.experience) params.append('experience', filters.experience);
  if (filters?.priceRange) params.append('price_range', filters.priceRange);
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.limit) params.append('limit', filters.limit.toString());

  const url = `${API_BASE_URL}/mentors?${params.toString()}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch mentors: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить ментора по ID
 */
export async function getMentor(id: number): Promise<Mentor> {
  const url = `${API_BASE_URL}/mentors/${id}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch mentor: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить отзывы о менторе
 */
export async function getMentorReviews(mentorId: number) {
  const url = `${API_BASE_URL}/mentors/${mentorId}/reviews`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch reviews: ${response.statusText}`);
  }

  return response.json();
}
