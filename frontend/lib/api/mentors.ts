/**
 * Mentors API Client
 * Клиент для работы с API менторов
 */

import { publicRequest } from './client'
import { SearchFilters } from '@/components/mentors/MentorSearchFilters'

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
    avatar_url?: string;
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

  searchParams.append('page', (params.page || 1).toString());
  searchParams.append('page_size', (params.page_size || 12).toString());

  if (params.query) searchParams.append('query', params.query);
  if (params.specialization) searchParams.append('specialization', params.specialization);
  if (params.minRate !== undefined) searchParams.append('min_rate', params.minRate.toString());
  if (params.maxRate !== undefined) searchParams.append('max_rate', params.maxRate.toString());
  if (params.minExperience !== undefined) searchParams.append('min_experience', params.minExperience.toString());
  if (params.maxExperience !== undefined) searchParams.append('max_experience', params.maxExperience.toString());
  if (params.isAvailable !== undefined) searchParams.append('is_available', params.isAvailable.toString());

  searchParams.append('sort_by', params.sortBy);
  searchParams.append('sort_order', params.sortOrder);

  return publicRequest<PaginatedResponse<Mentor>>(`/mentors/search?${searchParams.toString()}`);
}

/**
 * Получить список всех специализаций
 */
export async function getSpecializations(): Promise<string[]> {
  return publicRequest<string[]>('/mentors/specializations');
}

/**
 * Получить топ менторов по рейтингу
 */
export async function getTopRatedMentors(limit: number = 10): Promise<Mentor[]> {
  return publicRequest<Mentor[]>(`/mentors/top-rated?limit=${limit}`);
}

/**
 * Получить информацию о менторе по ID
 */
export async function getMentorById(id: number): Promise<Mentor> {
  try {
    return await publicRequest<Mentor>(`/mentors/${id}`);
  } catch (error) {
    if (error instanceof Error && error.message.includes('404')) {
      throw new Error('Mentor not found');
    }
    throw error;
  }
}

/**
 * Получить список всех менторов (без фильтрации)
 */
export async function getAllMentors(
  skip: number = 0,
  limit: number = 100
): Promise<Mentor[]> {
  return publicRequest<Mentor[]>(`/mentors?skip=${skip}&limit=${limit}`);
}

export interface MentorReview {
  id: number
  user_id: number
  user_name: string | null
  course_id: number | null
  reviewed_id: number | null
  rating: number
  comment: string | null
  created_at: string
  updated_at: string | null
}

/**
 * Получить отзывы о менторе по ID ментора
 */
export async function getMentorReviews(
  mentorId: number,
  page = 1,
  pageSize = 20
): Promise<PaginatedResponse<MentorReview>> {
  return publicRequest<PaginatedResponse<MentorReview>>(
    `/mentors/${mentorId}/reviews?page=${page}&page_size=${pageSize}`
  );
}
