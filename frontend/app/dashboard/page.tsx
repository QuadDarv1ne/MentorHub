"use client";
import React, { useState, useEffect } from 'react';
import { BookOpen, TrendingUp, Award, Clock, Calendar, ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface DashboardStats {
  total_courses: number;
  in_progress: number;
  completed: number;
  total_sessions: number;
  upcoming_sessions: number;
  total_reviews: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Получаем имя пользователя
      fetch('http://localhost:8000/api/v1/users/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => setUserName(data.full_name || data.email))
        .catch(() => {});

      // Имитация загрузки статистики (замените на реальный API)
      setTimeout(() => {
        setStats({
          total_courses: 12,
          in_progress: 3,
          completed: 8,
          total_sessions: 25,
          upcoming_sessions: 2,
          total_reviews: 15
        });
        setLoading(false);
      }, 500);
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!localStorage.getItem('access_token')) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Требуется авторизация</h2>
          <p className="text-gray-600 mb-6">Войдите в систему, чтобы просмотреть личный кабинет</p>
          <Link href="/auth/login" className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            Войти
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Добро пожаловать{userName ? `, ${userName}` : ''}! 👋
          </h1>
          <p className="mt-2 text-gray-600">Ваш личный кабинет на платформе MentorHub</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BookOpen className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Всего курсов</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{stats?.total_courses || 0}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <Link href="/courses" className="text-sm font-medium text-blue-600 hover:text-blue-500 flex items-center">
                Перейти к курсам
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingUp className="h-8 w-8 text-yellow-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">В процессе</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{stats?.in_progress || 0}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <Link href="/dashboard/progress" className="text-sm font-medium text-yellow-600 hover:text-yellow-500 flex items-center">
                Мой прогресс
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Award className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Завершено</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{stats?.completed || 0}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm text-gray-500">
                {stats?.completed ? `${Math.round((stats.completed / stats.total_courses) * 100)}% от общего числа` : 'Начните учиться!'}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-5 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Быстрые действия</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <Link href="/courses/stepik" className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
                  <BookOpen className="h-6 w-6 text-blue-600" />
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-900">Каталог курсов Stepik</h3>
                    <p className="text-sm text-gray-500">Просмотрите доступные курсы</p>
                  </div>
                </Link>

                <Link href="/mentors" className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
                  <Calendar className="h-6 w-6 text-purple-600" />
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-900">Найти ментора</h3>
                    <p className="text-sm text-gray-500">Забронируйте сессию с экспертом</p>
                  </div>
                </Link>

                <Link href="/profile" className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
                  <Award className="h-6 w-6 text-green-600" />
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-900">Мой профиль</h3>
                    <p className="text-sm text-gray-500">Редактировать информацию о себе</p>
                  </div>
                </Link>
              </div>
            </div>
          </div>

          {/* Upcoming Sessions */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-5 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Предстоящие сессии</h2>
            </div>
            <div className="p-6">
              {stats?.upcoming_sessions ? (
                <div className="space-y-4">
                  <div className="flex items-start p-4 border border-gray-200 rounded-lg">
                    <Clock className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">Консультация по React</p>
                      <p className="text-sm text-gray-500">Сегодня в 15:00 • с Иваном Петровым</p>
                    </div>
                  </div>
                  <div className="flex items-start p-4 border border-gray-200 rounded-lg">
                    <Clock className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">Ревью кода</p>
                      <p className="text-sm text-gray-500">Завтра в 10:00 • с Марией Смирновой</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500 mb-4">У вас нет предстоящих сессий</p>
                  <Link href="/mentors" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                    Найти ментора
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8 bg-white shadow rounded-lg">
          <div className="px-6 py-5 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Недавняя активность</h2>
          </div>
          <div className="p-6">
            <div className="flow-root">
              <ul className="-mb-8">
                <li className="relative pb-8">
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                        <BookOpen className="h-5 w-5 text-white" />
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div>
                        <p className="text-sm text-gray-900">
                          Начали курс <span className="font-medium">Основы Python</span>
                        </p>
                        <p className="text-sm text-gray-500">2 часа назад</p>
                      </div>
                    </div>
                  </div>
                </li>
                <li className="relative pb-8">
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                        <Award className="h-5 w-5 text-white" />
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div>
                        <p className="text-sm text-gray-900">
                          Завершили курс <span className="font-medium">JavaScript для начинающих</span>
                        </p>
                        <p className="text-sm text-gray-500">Вчера</p>
                      </div>
                    </div>
                  </div>
                </li>
                <li className="relative">
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center ring-8 ring-white">
                        <Calendar className="h-5 w-5 text-white" />
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div>
                        <p className="text-sm text-gray-900">
                          Забронировали сессию с <span className="font-medium">Иваном Петровым</span>
                        </p>
                        <p className="text-sm text-gray-500">3 дня назад</p>
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}