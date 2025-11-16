"use client";
import React, { useEffect, useState } from 'react';
import { getSimilarCourses, type SimilarCourse } from '@/lib/api/courses';
import { getCourse, type StepikCourse } from '@/lib/api/stepik';

export default function SimilarCourses({ courseId }: { courseId: number }) {
  const [items, setItems] = useState<SimilarCourse[]>([]);
  const [details, setDetails] = useState<Record<number, Pick<StepikCourse, 'id' | 'title' | 'cover'>> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getSimilarCourses(courseId)
      .then(async (data) => {
        if (!mounted) return;
        setItems(data);
        // подгружаем названия/обложки с Stepik для карточек
        try {
          const uniqueIds = Array.from(new Set(data.map(d => d.course_id)));
          const courses = await Promise.all(uniqueIds.map(id => getCourse(id).catch(() => null)));
          const map: Record<number, Pick<StepikCourse, 'id' | 'title' | 'cover'>> = {};
          courses.filter(Boolean).forEach((c: any) => {
            map[c.id] = { id: c.id, title: c.title, cover: c.cover };
          });
          if (mounted) setDetails(map);
        } catch {
          // игнорируем ошибки деталей
        }
      })
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
                <a href={`/courses/stepik/${it.course_id}`} className="flex items-center gap-3">
                  <div className="w-12 h-8 bg-gray-100 rounded overflow-hidden">
                    {details?.[it.course_id]?.cover ? (
                      <img src={details[it.course_id].cover} alt={details[it.course_id].title} className="w-full h-full object-cover" />
                    ) : null}
                  </div>
                  <div>
                    <div className="text-sm text-gray-900 font-medium">
                      {details?.[it.course_id]?.title || `Курс #${it.course_id}`}
                    </div>
                    <div className="text-xs text-gray-500">Отзывов: {it.total_reviews}</div>
                  </div>
                </a>
                <div className="text-sm font-medium">⭐ {it.average_rating.toFixed(1)}</div>
              </li>
            ))}
          </ul>
        )
      )}
    </div>
  );
}
