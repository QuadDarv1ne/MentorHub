"use client";

import { useState, useCallback } from 'react';
import { SearchFilters } from '@/components/mentors/MentorSearchFilters';

interface Mentor {
  id: number;
  user_id: number;
  specialization: string;
  bio: string;
  experience_years: number;
  hourly_rate: number;
  rating: number;
  total_reviews: number;
  is_available: boolean;
  user: {
    id: number;
    full_name: string;
    email: string;
  };
}

interface SearchResponse {
  items: Mentor[];
  total: number;
  page: number;
  page_size: number;
}

export function useMentorSearch() {
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [specializations, setSpecializations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);

  const fetchSpecializations = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/mentors/specializations');
      if (response.ok) {
        const data = await response.json();
        setSpecializations(data);
      }
    } catch (err) {
      console.error('Failed to fetch specializations:', err);
    }
  }, []);

  const searchMentors = useCallback(async (filters: SearchFilters, currentPage: number = 1) => {
    setLoading(true);
    setError(null);

    try {
      // Build query params
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', pageSize.toString());

      if (filters.query) params.append('query', filters.query);
      if (filters.specialization) params.append('specialization', filters.specialization);
      if (filters.minRate !== undefined) params.append('min_rate', filters.minRate.toString());
      if (filters.maxRate !== undefined) params.append('max_rate', filters.maxRate.toString());
      if (filters.minExperience !== undefined) params.append('min_experience', filters.minExperience.toString());
      if (filters.maxExperience !== undefined) params.append('max_experience', filters.maxExperience.toString());
      if (filters.isAvailable !== undefined) params.append('is_available', filters.isAvailable.toString());
      params.append('sort_by', filters.sortBy);
      params.append('sort_order', filters.sortOrder);

      const response = await fetch(`/api/v1/mentors/search?${params.toString()}`);

      if (!response.ok) {
        throw new Error('Failed to search mentors');
      }

      const data: SearchResponse = await response.json();
      setMentors(data.items);
      setTotal(data.total);
      setPage(data.page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setMentors([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  const fetchTopRated = useCallback(async (limit: number = 10) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/mentors/top-rated?limit=${limit}`);

      if (!response.ok) {
        throw new Error('Failed to fetch top rated mentors');
      }

      const data: Mentor[] = await response.json();
      setMentors(data);
      setTotal(data.length);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setMentors([]);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    mentors,
    specializations,
    loading,
    error,
    total,
    page,
    pageSize,
    searchMentors,
    fetchSpecializations,
    fetchTopRated,
  };
}
