"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Review {
  id: number;
  user_id: number;
  user_name?: string | null;
  rating: number;
  comment?: string;
  created_at: string;
}

interface Paginated<T> {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  data: T[];
}

export default function ReviewList({ courseId }: { courseId: number }) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchReviews = async () => {
      setIsLoading(true);
      try {
        const res = await fetch(`/api/v1/courses/${courseId}/reviews?page=${page}&page_size=10`);
        if (!res.ok) throw new Error('Failed to load reviews');
        const data: Paginated<Review> = await res.json();
        setReviews(data.data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReviews();
  }, [courseId, page]);

  if (isLoading) return <div>Загрузка отзывов...</div>;
  if (!reviews.length) return <div>Пока нет отзывов. Будьте первым!</div>;

  return (
    <div className="space-y-4">
      {reviews.map((r) => (
        <div key={r.id} className="bg-white p-4 rounded shadow">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-medium">{r.user_name ? r.user_name : `Пользователь #${r.user_id}`}</div>
            <div className="text-sm text-yellow-500">{r.rating} ★</div>
          </div>
          {r.comment && <p className="text-gray-700">{r.comment}</p>}
          <div className="text-xs text-gray-400 mt-2">{new Date(r.created_at).toLocaleString()}</div>
        </div>
      ))}

      {/* Пагинация (простая) */}
      <div className="flex justify-between items-center">
        <button
          className="px-3 py-1 bg-gray-100 rounded disabled:opacity-50"
          disabled={page <= 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          Предыдущая
        </button>
        <div className="text-sm text-gray-600">Страница {page}</div>
        <button
          className="px-3 py-1 bg-gray-100 rounded"
          onClick={() => setPage((p) => p + 1)}
        >
          Следующая
        </button>
      </div>
    </div>
  );
}