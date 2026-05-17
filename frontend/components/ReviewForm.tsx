"use client";

import { useState } from 'react';
import { apiRequest } from '@/lib/api/client';

export default function ReviewForm({ courseId, onSuccess }: { courseId: number; onSuccess?: () => void }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await apiRequest(`/courses/${courseId}/reviews`, {
        method: 'POST',
        body: JSON.stringify({ rating, comment }),
      });

      setComment('');
      setRating(5);
      onSuccess?.();
    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        setError('Требуется авторизация. Пожалуйста, войдите.');
      } else {
        setError(err instanceof Error ? err.message : 'Ошибка сети');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="bg-white p-4 rounded shadow">
      <h3 className="font-semibold mb-2">Оставьте отзыв</h3>
      <div className="flex items-center gap-4 mb-2">
        <label htmlFor="review-rating" className="text-sm">Оценка:</label>
        <select id="review-rating" value={rating} onChange={(e) => setRating(Number(e.target.value))} className="border px-2 py-1 rounded">
          {[5,4,3,2,1].map((n) => (
            <option key={n} value={n}>{n} ★</option>
          ))}
        </select>
      </div>
      <div className="mb-2">
        <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={4} className="w-full border rounded p-2" placeholder="Ваш отзыв (необязательно)"></textarea>
      </div>
      {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
      <div className="flex justify-end">
        <button disabled={isSubmitting} className="px-4 py-2 bg-primary-600 text-white rounded">
          {isSubmitting ? 'Отправка...' : 'Отправить'}
        </button>
      </div>
    </form>
  );
}
