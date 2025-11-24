"use client";

import React, { useEffect, useState } from 'react';
import { getMyProgress, upsertProgress } from '@/lib/api/progress';

export default function ProgressTracker({ courseId }: { courseId: number }) {
  const [percent, setPercent] = useState<number>(0);
  const [lastSavedPercent, setLastSavedPercent] = useState<number>(0);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    let mounted = true;
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    setIsAuthenticated(Boolean(token));
    (async () => {
      try {
        const res = await getMyProgress(courseId);
        if (!mounted) return;
        // If there is an existing lesson-level record, pick first, otherwise pick course-level
        const existing = (Array.isArray(res) ? res[0] : null) || null;
        if (existing) {
          const p = existing.progress_percent ?? 0;
          setPercent(p);
          setLastSavedPercent(p);
        }
      } catch {
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
    setSuccess(null);
    try {
      const payload = { course_id: courseId, progress_percent: percent };
      await upsertProgress(payload);
      setLastSavedPercent(percent);
      setSuccess('Сохранено');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка при сохранении');
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
    setSuccess(null);
    try {
      await upsertProgress({ course_id: courseId, progress_percent: 100 });
      setPercent(100);
      setLastSavedPercent(100);
      setSuccess('Сохранено');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка при сохранении');
    } finally {
      setIsSaving(false);
    }
  };

  const cancelChanges = () => {
    setPercent(lastSavedPercent);
    setError(null);
    setSuccess('Изменения отменены');
  };

  return (
    <div className="bg-white p-4 rounded shadow mt-6">
      <h3 className="font-semibold mb-2">Прогресс по курсу</h3>
      <div className="mb-2">
        <progress max="100" value={percent} className="w-full h-4 rounded">
          {percent}%
        </progress>
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
        <button onClick={cancelChanges} disabled={isSaving} className="px-3 py-1 bg-gray-200 text-gray-800 rounded">
          Отменить
        </button>
      </div>
      <div aria-live="polite" className="text-sm mt-2">
        {error && <div className="text-red-600">{error}</div>}
        {success && <div className="text-green-600">{success}</div>}
      </div>
      {!isAuthenticated && (
        <div className="text-sm text-gray-600 mt-3">
          Для сохранения прогресса <a href="/auth/login" className="text-primary-600 hover:underline">войдите в аккаунт</a>.
        </div>
      )}
    </div>
  );
}
