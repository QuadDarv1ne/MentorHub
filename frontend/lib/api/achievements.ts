export interface Achievement {
  id: number;
  user_id: number;
  title: string;
  description: string;
  icon: string;
  earned_at: string;
}

/**
 * Получить все достижения текущего пользователя
 */
export async function getMyAchievements(): Promise<Achievement[]> {
  // Since there's no specific achievements endpoint in the backend yet,
  // we'll return mock data for now
  return [
    { id: 1, user_id: 1, title: '7-дневная серия', description: 'Учитесь 7 дней подряд', icon: '🏆', earned_at: '2024-01-15' },
    { id: 2, user_id: 1, title: '5 курсов', description: 'Завершено 5 курсов', icon: '📚', earned_at: '2024-01-10' },
    { id: 3, user_id: 1, title: 'Отличник', description: '4.8+ рейтинг в тестах', icon: '⭐', earned_at: '2024-01-05' },
    { id: 4, user_id: 1, title: 'Быстрый старт', description: 'Первые 3 дня обучения', icon: '🚀', earned_at: '2024-01-01' }
  ];
}