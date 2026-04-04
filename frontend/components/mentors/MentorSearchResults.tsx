"use client";

import React from 'react';
import { Star, Clock, DollarSign, CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';

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

interface MentorSearchResultsProps {
  mentors: Mentor[];
  loading: boolean;
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

export default function MentorSearchResults({
  mentors,
  loading,
  total,
  page,
  pageSize,
  onPageChange
}: MentorSearchResultsProps) {
  const totalPages = Math.ceil(total / pageSize);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (mentors.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400 text-lg">
          Менторы не найдены. Попробуйте изменить параметры поиска.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
        Найдено менторов: {total}
      </div>

      {/* Mentor Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {mentors.map((mentor) => (
          <div
            key={mentor.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  {mentor.user.full_name}
                </h3>
                <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                  {mentor.specialization}
                </p>
              </div>
              
              {mentor.is_available ? (
                <CheckCircle className="w-6 h-6 text-green-500" title="Доступен" />
              ) : (
                <XCircle className="w-6 h-6 text-gray-400" title="Недоступен" />
              )}
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
                  {mentor.rating?.toFixed(1) ?? 'N/A'}
                </span>
                <span className="text-gray-500 dark:text-gray-400">
                  ({mentor.total_reviews} отзывов)
                </span>
              </div>

              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Clock className="w-4 h-4" />
                <span>{mentor.experience_years} лет опыта</span>
              </div>

              <div className="flex items-center gap-2 text-sm">
                <DollarSign className="w-4 h-4 text-green-600 dark:text-green-400" />
                <span className="font-semibold text-gray-900 dark:text-white">
                  {mentor.hourly_rate} ₽/час
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Link
                href={`/dashboard/mentors/${mentor.id}`}
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
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Назад
          </button>

          <div className="flex gap-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (page <= 3) {
                pageNum = i + 1;
              } else if (page >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = page - 2 + i;
              }

              return (
                <button
                  key={pageNum}
                  onClick={() => onPageChange(pageNum)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    page === pageNum
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page === totalPages}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Вперёд
          </button>
        </div>
      )}
    </div>
  );
}
