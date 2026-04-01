"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Star, Search, Filter, TrendingUp } from 'lucide-react';
import { getAllMentors, getTopRatedMentors, Mentor } from '@/lib/api/mentors';

export default function MentorsPage() {
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [topRated, setTopRated] = useState<Mentor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadMentors();
  }, []);

  const loadMentors = async () => {
    try {
      setLoading(true);
      const [allMentors, topMentors] = await Promise.all([
        getAllMentors(0, 12),
        getTopRatedMentors(6)
      ]);
      setMentors(allMentors);
      setTopRated(topMentors);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load mentors');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      window.location.href = `/mentors/search?query=${encodeURIComponent(searchQuery)}`;
    } else {
      window.location.href = '/mentors/search';
    }
  };

  if (loading) {
    return (
      <main className="container mx-auto max-w-7xl px-4 py-10">
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="container mx-auto max-w-7xl px-4 py-10">
        <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-6">
          <h2 className="text-xl font-bold text-red-800 dark:text-red-200 mb-2">
            Ошибка загрузки
          </h2>
          <p className="text-red-600 dark:text-red-300">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="container mx-auto max-w-7xl px-4 py-10">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
          Найдите идеального ментора
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          {mentors.length}+ профессионалов готовы помочь вам достичь целей
        </p>

        {/* Search Bar */}
        <div className="max-w-2xl mx-auto">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Поиск по имени, специальности или навыкам..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-12 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white text-lg"
              />
            </div>
            <button
              onClick={handleSearch}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Поиск
            </button>
            <Link
              href="/mentors/search"
              className="flex items-center gap-2 px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              <Filter className="w-5 h-5" />
              Фильтры
            </Link>
          </div>
        </div>
      </div>

      {/* Top Rated Mentors */}
      {topRated.length > 0 && (
        <section className="mb-12">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="w-6 h-6 text-yellow-500" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Топ менторов
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topRated.map((mentor) => (
              <MentorCard key={mentor.id} mentor={mentor} featured />
            ))}
          </div>
        </section>
      )}

      {/* All Mentors */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Все менторы
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mentors.map((mentor) => (
            <MentorCard key={mentor.id} mentor={mentor} />
          ))}
        </div>

        {/* View All Button */}
        <div className="text-center mt-8">
          <Link
            href="/mentors/search"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Посмотреть всех менторов
            <Search className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Tips Section */}
      <section className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 rounded-lg p-8">
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
      </section>
    </main>
  );
}

// Mentor Card Component
function MentorCard({ mentor, featured = false }: { mentor: Mentor; featured?: boolean }) {
  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 ${
        featured ? 'ring-2 ring-yellow-400' : ''
      }`}
    >
      {featured && (
        <div className="flex items-center gap-1 text-yellow-500 text-sm font-medium mb-2">
          <Star className="w-4 h-4 fill-current" />
          Топ ментор
        </div>
      )}

      {/* Header */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
          {mentor.user.full_name}
        </h3>
        <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">
          {mentor.specialization}
        </p>
      </div>

      {/* Bio */}
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
        {mentor.bio}
      </p>

      {/* Stats */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm">
          <Star className="w-4 h-4 text-yellow-500" />
          <span className="font-medium text-gray-900 dark:text-white">
            {mentor.rating.toFixed(1)}
          </span>
          <span className="text-gray-500 dark:text-gray-400">
            ({mentor.total_reviews} отзывов)
          </span>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <span>💼 {mentor.experience_years} лет опыта</span>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <span className="font-semibold text-green-600 dark:text-green-400">
            {mentor.hourly_rate} ₽/час
          </span>
        </div>

        {mentor.is_available && (
          <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            Доступен
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Link
          href={`/mentors/${mentor.id}`}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center text-sm font-medium"
        >
          Подробнее
        </Link>
        <Link
          href={`/dashboard/sessions/book?mentor_id=${mentor.id}`}
          className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-center text-sm font-medium"
        >
          Забронировать
        </Link>
      </div>
    </div>
  );
}
