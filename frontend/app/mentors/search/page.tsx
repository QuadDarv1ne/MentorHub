"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import MentorSearchFilters, { SearchFilters } from '@/components/mentors/MentorSearchFilters';
import MentorSearchResults from '@/components/mentors/MentorSearchResults';
import { useMentorSearch } from '@/hooks/useMentorSearch';

export default function MentorSearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const {
    mentors,
    specializations,
    loading,
    error,
    total,
    page,
    pageSize,
    searchMentors,
    fetchSpecializations,
  } = useMentorSearch();

  const [currentFilters, setCurrentFilters] = useState<SearchFilters>({
    sortBy: 'rating',
    sortOrder: 'desc',
  });

  // Load specializations on mount
  useEffect(() => {
    fetchSpecializations();
  }, [fetchSpecializations]);

  // Parse URL params and perform initial search
  useEffect(() => {
    const isValidSortBy = (val: string): val is SearchFilters['sortBy'] =>
      ['rating', 'price', 'experience', 'name'].includes(val)
    
    const isValidSortOrder = (val: string): val is SearchFilters['sortOrder'] =>
      ['asc', 'desc'].includes(val)

    const rawSortBy = searchParams.get('sort_by') || 'rating'
    const rawSortOrder = searchParams.get('sort_order') || 'desc'

    const filters: SearchFilters = {
      query: searchParams.get('query') || undefined,
      specialization: searchParams.get('specialization') || undefined,
      minRate: searchParams.get('min_rate') ? Number(searchParams.get('min_rate')) : undefined,
      maxRate: searchParams.get('max_rate') ? Number(searchParams.get('max_rate')) : undefined,
      minExperience: searchParams.get('min_experience') ? Number(searchParams.get('min_experience')) : undefined,
      maxExperience: searchParams.get('max_experience') ? Number(searchParams.get('max_experience')) : undefined,
      isAvailable: searchParams.get('is_available') ? searchParams.get('is_available') === 'true' : undefined,
      sortBy: isValidSortBy(rawSortBy) ? rawSortBy : 'rating',
      sortOrder: isValidSortOrder(rawSortOrder) ? rawSortOrder : 'desc',
    };

    setCurrentFilters(filters);
    searchMentors(filters, 1);
  }, [searchParams]);

  const handleSearch = (filters: SearchFilters) => {
    setCurrentFilters(filters);
    
    // Update URL params
    const params = new URLSearchParams();
    if (filters.query) params.set('query', filters.query);
    if (filters.specialization) params.set('specialization', filters.specialization);
    if (filters.minRate !== undefined) params.set('min_rate', filters.minRate.toString());
    if (filters.maxRate !== undefined) params.set('max_rate', filters.maxRate.toString());
    if (filters.minExperience !== undefined) params.set('min_experience', filters.minExperience.toString());
    if (filters.maxExperience !== undefined) params.set('max_experience', filters.maxExperience.toString());
    if (filters.isAvailable !== undefined) params.set('is_available', filters.isAvailable.toString());
    params.set('sort_by', filters.sortBy);
    params.set('sort_order', filters.sortOrder);

    router.push(`/mentors/search?${params.toString()}`);
    searchMentors(filters, 1);
  };

  const handlePageChange = (newPage: number) => {
    searchMentors(currentFilters, newPage);
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <main className="container mx-auto max-w-7xl px-4 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          Поиск менторов
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          Найдите идеального ментора для достижения ваших целей
        </p>
      </div>

      {/* Search Filters */}
      <MentorSearchFilters
        onSearch={handleSearch}
        specializations={specializations}
      />

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4 mb-6">
          <p className="text-red-800 dark:text-red-200">
            Ошибка при загрузке менторов: {error}
          </p>
        </div>
      )}

      {/* Search Results */}
      <MentorSearchResults
        mentors={mentors}
        loading={loading}
        total={total}
        page={page}
        pageSize={pageSize}
        onPageChange={handlePageChange}
      />

      {/* Tips Section */}
      {!loading && mentors.length > 0 && (
        <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 rounded-lg p-8">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
            💡 Советы по выбору ментора
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-2xl mb-2">⭐</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                Смотрите отзывы
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Рейтинг и количество отзывов показывают качество работы ментора
              </p>
            </div>
            <div>
              <div className="text-2xl mb-2">🎯</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                Выбирайте по специальности
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Ищите менторов, чьи навыки совпадают с вашими целями обучения
              </p>
            </div>
            <div>
              <div className="text-2xl mb-2">📅</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                Проверьте доступность
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Убедитесь, что график ментора соответствует вашему времени
              </p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
