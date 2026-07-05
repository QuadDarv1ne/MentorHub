"use client";

import { useState, useCallback } from 'react';
import { SearchFilters } from '@/components/mentors/MentorSearchFilters';
import { logger } from '@/lib/utils/logger';
import {
  searchMentors as apiSearchMentors,
  getSpecializations as apiGetSpecializations,
  getTopRatedMentors as apiGetTopRatedMentors,
  Mentor,
} from '@/lib/api/mentors';

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
      const data = await apiGetSpecializations();
      setSpecializations(data);
    } catch (err) {
      logger.error('Failed to fetch specializations:', err as Error);
    }
  }, []);

  const searchMentors = useCallback(async (filters: SearchFilters, currentPage: number = 1) => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiSearchMentors({
        ...filters,
        page: currentPage,
        page_size: pageSize,
      });

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
      const data = await apiGetTopRatedMentors(limit);
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
