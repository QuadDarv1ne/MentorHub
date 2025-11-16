"use client";
import React, { useEffect, useState } from 'react';
import ProgressList, { type ProgressItem } from '@/components/ProgressList';
import { getMyProgress } from '@/lib/api/progress';

export default function ProgressDashboardPage() {
  const [items, setItems] = useState<ProgressItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = typeof window !== 'undefined' && !!localStorage.getItem('access_token');

  useEffect(() => {
    if (!isAuthenticated) return;
    setLoading(true);
    getMyProgress()
      .then((data) => setItems(data))
      .catch((e) => setError(e.message || 'Не удалось загрузить прогресс'))
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <h1 className="text-2xl font-semibold mb-4">Мой прогресс</h1>
        <p>
          Для просмотра прогресса войдите в аккаунт.
          <a className="text-blue-600 underline ml-1" href="/login">Войти</a>
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Мой прогресс</h1>
      {loading && <div role="status">Загрузка…</div>}
      {error && <div role="alert" className="text-red-600">{error}</div>}
      {!loading && !error && <ProgressList items={items} />}
    </div>
  );
}
