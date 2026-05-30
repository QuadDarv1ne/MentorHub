"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Search, Filter, X } from 'lucide-react';

interface MentorSearchFiltersProps {
  onSearch: (filters: SearchFilters) => void;
  specializations: string[];
}

export interface SearchFilters {
  query?: string;
  specialization?: string;
  minRate?: number;
  maxRate?: number;
  minExperience?: number;
  maxExperience?: number;
  isAvailable?: boolean;
  sortBy: 'rating' | 'price' | 'experience' | 'name';
  sortOrder: 'asc' | 'desc';
}

export default function MentorSearchFilters({ onSearch, specializations }: MentorSearchFiltersProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    sortBy: 'rating',
    sortOrder: 'desc'
  });

  const handleFilterChange = <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => {
    setFilters(prev => ({
      ...prev,
      [key]: value === '' ? undefined : value
    }));
  };

  const handleSearch = useCallback(() => {
    onSearch(filters);
  }, [onSearch, filters]);

  const handleReset = () => {
    const resetFilters: SearchFilters = {
      sortBy: 'rating',
      sortOrder: 'desc'
    };
    setFilters(resetFilters);
    onSearch(resetFilters);
  };

  useEffect(() => {
    // Auto-search on filter change (debounced)
    const timer = setTimeout(() => {
      handleSearch();
    }, 500);

    return () => clearTimeout(timer);
  }, [filters, handleSearch]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
      {/* Search Bar */}
      <div className="flex gap-4 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Поиск по имени или специализации..."
            value={filters.query || ''}
            onChange={(e) => handleFilterChange('query', e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
        
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          <Filter className="w-5 h-5" />
          Фильтры
        </button>

        {Object.keys(filters).length > 2 && (
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
          >
            <X className="w-5 h-5" />
            Сбросить
          </button>
        )}
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          {/* Specialization */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Специализация
            </label>
            <select
              value={filters.specialization || ''}
              onChange={(e) => handleFilterChange('specialization', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">Все специализации</option>
              {specializations.map(spec => (
                <option key={spec} value={spec}>{spec}</option>
              ))}
            </select>
          </div>

          {/* Price Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Цена (₽/час)
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="От"
                value={filters.minRate || ''}
                onChange={(e) => handleFilterChange('minRate', e.target.value ? Number(e.target.value) : undefined)}
                className="w-1/2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
              <input
                type="number"
                placeholder="До"
                value={filters.maxRate || ''}
                onChange={(e) => handleFilterChange('maxRate', e.target.value ? Number(e.target.value) : undefined)}
                className="w-1/2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Experience Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Опыт (лет)
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="От"
                value={filters.minExperience || ''}
                onChange={(e) => handleFilterChange('minExperience', e.target.value ? Number(e.target.value) : undefined)}
                className="w-1/2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
              <input
                type="number"
                placeholder="До"
                value={filters.maxExperience || ''}
                onChange={(e) => handleFilterChange('maxExperience', e.target.value ? Number(e.target.value) : undefined)}
                className="w-1/2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Availability */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Доступность
            </label>
            <select
              value={filters.isAvailable === undefined ? '' : filters.isAvailable.toString()}
              onChange={(e) => handleFilterChange('isAvailable', e.target.value === '' ? undefined : e.target.value === 'true')}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">Все</option>
              <option value="true">Только доступные</option>
              <option value="false">Недоступные</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Сортировка
            </label>
            <select
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value as 'name' | 'rating' | 'price' | 'experience')}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="rating">По рейтингу</option>
              <option value="price">По цене</option>
              <option value="experience">По опыту</option>
              <option value="name">По имени</option>
            </select>
          </div>

          {/* Sort Order */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Порядок
            </label>
            <select
              value={filters.sortOrder}
              onChange={(e) => handleFilterChange('sortOrder', e.target.value as 'desc' | 'asc')}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="desc">По убыванию</option>
              <option value="asc">По возрастанию</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
}
