/**
 * Mentors API Client
 * Клиент для работы с API менторов
 */

import { SearchFilters } from '@/components/mentors/MentorSearchFilters';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Mentor {
  id: number;
  user_id: number;
  specialization: string;
  bio: string;
  experience_years: number;
  hourly_rate: number;
  rating: number;
  total_reviews: number;
  is_available: boolean;
  created_at: string;
  updated_at: string;
  user: {
    id: number;
    full_name: string;
    email: string;
    role: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface MentorSearchParams extends SearchFilters {
  page?: number;
  page_size?: number;
}

/**
 * Поиск менторов с фильтрацией
 */
export async function searchMentors(
  params: MentorSearchParams
): Promise<PaginatedResponse<Mentor>> {
  const searchParams = new URLSearchParams();

  // Pagination
  searchParams.append('page', (params.page || 1).toString());
  searchParams.append('page_size', (params.page_size || 12).toString());

  // Filters
  if (params.query) searchParams.append('query', params.query);
  if (params.specialization) searchParams.append('specialization', params.specialization);
  if (params.minRate !== undefined) searchParams.append('min_rate', params.minRate.toString());
  if (params.maxRate !== undefined) searchParams.append('max_rate', params.maxRate.toString());
  if (params.minExperience !== undefined) searchParams.append('min_experience', params.minExperience.toString());
  if (params.maxExperience !== undefined) searchParams.append('max_experience', params.maxExperience.toString());
  if (params.isAvailable !== undefined) searchParams.append('is_available', params.isAvailable.toString());

  // Sorting
  searchParams.append('sort_by', params.sortBy);
  searchParams.append('sort_order', params.sortOrder);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/mentors/search?${searchParams.toString()}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store', // Disable caching for search results
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to search mentors: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить список всех специализаций
 */
export async function getSpecializations(): Promise<string[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/mentors/specializations`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      next: { revalidate: 3600 }, // Cache for 1 hour
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch specializations: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить топ менторов по рейтингу
 */
export async function getTopRatedMentors(limit: number = 10): Promise<Mentor[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/mentors/top-rated?limit=${limit}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      next: { revalidate: 1800 }, // Cache for 30 minutes
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch top rated mentors: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить информацию о менторе по ID
 */
export async function getMentorById(id: number): Promise<Mentor> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/mentors/${id}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      next: { revalidate: 900 }, // Cache for 15 minutes
    }
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Mentor not found');
    }
    throw new Error(`Failed to fetch mentor: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить список всех менторов (без фильтрации)
 */
export async function getAllMentors(
  skip: number = 0,
  limit: number = 100
): Promise<Mentor[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/mentors?skip=${skip}&limit=${limit}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      next: { revalidate: 900 }, // Cache for 15 minutes
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch mentors: ${response.statusText}`);
  }

  return response.json();
}
