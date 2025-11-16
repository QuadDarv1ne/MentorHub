import React from 'react';

export type ProgressItem = {
  id: number;
  course_id: number;
  lesson_id?: number | null;
  progress_percent: number;
  completed: boolean;
};

type Props = {
  items: ProgressItem[];
};

export default function ProgressList({ items }: Props) {
  if (!items || items.length === 0) {
    return <div role="status">Пока нет данных о прогрессе</div>;
  }

  return (
    <div className="space-y-4">
      {items.map((it) => (
        <div key={it.id} className="border rounded p-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Курс #{it.course_id}{it.lesson_id ? ` · Урок #${it.lesson_id}` : ''}</div>
              <div className="text-base font-medium">{it.completed ? 'Завершено' : 'В процессе'}</div>
            </div>
            <div className="w-40">
              <div className="text-right text-sm">{it.progress_percent}%</div>
              <progress className="w-full h-2" max={100} value={it.progress_percent} aria-label={`Прогресс ${it.progress_percent}%`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
