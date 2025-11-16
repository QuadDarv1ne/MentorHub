"use client";
import React, { useEffect, useState } from 'react';
import { getSimilarCourses, type SimilarCourse } from '@/lib/api/courses';

export default function SimilarCourses({ courseId }: { courseId: number }) {
  const [items, setItems] = useState<SimilarCourse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getSimilarCourses(courseId)
      .then((data) => { if (mounted) setItems(data); })
      .catch((e) => { if (mounted) setError(e.message || 'Не удалось получить рекомендации'); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [courseId]);

  return (
    <div className="bg-white p-4 rounded shadow mt-6">
      <h3 className="font-semibold mb-3">Похожие курсы</h3>
      {loading && <div role="status">Загрузка…</div>}
      {error && <div role="alert" className="text-red-600">{error}</div>}
      {!loading && !error && (
        items.length === 0 ? (
          <div className="text-sm text-gray-600">Пока нет рекомендаций</div>
        ) : (
          <ul className="space-y-2">
            {items.map((it) => (
              <li key={it.course_id} className="flex items-center justify-between border rounded p-2">
                <div>
                  <div className="text-sm text-gray-700">Курс #{it.course_id}</div>
                  <div className="text-xs text-gray-500">Отзывов: {it.total_reviews}</div>
                </div>
                <div className="text-sm font-medium">⭐ {it.average_rating.toFixed(1)}</div>
              </li>
            ))}
          </ul>
        )
      )}
    </div>
  );
}
