"use client";

import React, { useEffect, useState } from 'react';
import { getMyProgress, upsertProgress } from '@/lib/api/progress';

export default function ProgressTracker({ courseId }: { courseId: number }) {
  const [items, setItems] = useState<any[]>([]);
  const [percent, setPercent] = useState<number>(0);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    let mounted = true;
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    setIsAuthenticated(Boolean(token));
    (async () => {
      try {
        const res = await getMyProgress(courseId);
        if (!mounted) return;
        setItems(Array.isArray(res) ? res : []);
        // If there is an existing lesson-level record, pick first, otherwise pick course-level
        const existing = (Array.isArray(res) ? res[0] : null) || null;
        if (existing) setPercent(existing.progress_percent ?? 0);
      } catch (e) {
        // ignore for unauthenticated
      }
    })();
    return () => { mounted = false; };
  }, [courseId]);

  const save = async () => {
    if (!isAuthenticated) {
      setError('Требуется авторизация для сохранения прогресса');
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      const payload = { course_id: courseId, progress_percent: percent };
      const saved = await upsertProgress(payload);
      setItems([saved]);
    } catch (e: any) {
      setError(e.message || 'Ошибка при сохранении');
    } finally {
      setIsSaving(false);
    }
  };

  const markCompleted = async () => {
    if (!isAuthenticated) {
      setError('Требуется авторизация для сохранения прогресса');
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      const payload = { course_id: courseId, progress_percent: 100, completed: true };
      const saved = await upsertProgress(payload);
      setItems([saved]);
      setPercent(100);
    } catch (e: any) {
      setError(e.message || 'Ошибка при сохранении');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow mt-6">
      <h3 className="font-semibold mb-2">Прогресс по курсу</h3>
      <div className="mb-2">
        <div className="w-full bg-gray-200 rounded h-4 overflow-hidden">
          <div className="bg-primary-600 h-4" style={{ width: `${percent}%` }} />
        </div>
        <div className="text-sm text-gray-600 mt-1">{percent}%</div>
      </div>

      <div className="flex items-center gap-3">
        <label htmlFor={`progress-range-${courseId}`} className="sr-only">Прогресс</label>
        <input
          id={`progress-range-${courseId}`}
          aria-label="Прогресс по курсу"
          type="range"
          min={0}
          max={100}
          value={percent}
          onChange={(e) => setPercent(Number(e.target.value))}
          className="flex-1"
          disabled={!isAuthenticated}
        />
        <button onClick={save} disabled={isSaving} className="px-3 py-1 bg-primary-600 text-white rounded">
          {isSaving ? 'Сохранение...' : 'Сохранить'}
        </button>
        <button onClick={markCompleted} disabled={isSaving} className="px-3 py-1 bg-green-600 text-white rounded">
          Пометить завершённым
        </button>
      </div>
      {error && <div className="text-sm text-red-600 mt-2">{error}</div>}
      {!isAuthenticated && (
        <div className="text-sm text-gray-600 mt-3">
          Для сохранения прогресса <a href="/auth/login" className="text-primary-600 hover:underline">войдите в аккаунт</a>.
        </div>
      )}
    </div>
  );
}
