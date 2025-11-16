"use client";
import React, { useState, useEffect } from 'react';
import { Calendar, Clock, User, Video, X, CheckCircle, AlertCircle, MapPin } from 'lucide-react';

interface Session {
  id: number;
  mentor_name: string;
  topic: string;
  scheduled_time: string;
  duration: number;
  price: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  meeting_link?: string;
}

type TabType = 'upcoming' | 'past';

export default function SessionsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('upcoming');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, [activeTab]);

  const fetchSessions = async () => {
    setLoading(true);
    
    // Имитация API запроса
    setTimeout(() => {
      const mockSessions: Session[] = activeTab === 'upcoming' ? [
        {
          id: 1,
          mentor_name: 'Иван Петров',
          topic: 'Консультация по React и TypeScript',
          scheduled_time: '2024-02-15T15:00:00',
          duration: 60,
          price: 50,
          status: 'confirmed',
          meeting_link: 'https://meet.example.com/abc123'
        },
        {
          id: 2,
          mentor_name: 'Анна Смирнова',
          topic: 'Code Review и архитектура Backend',
          scheduled_time: '2024-02-18T10:00:00',
          duration: 90,
          price: 90,
          status: 'pending'
        },
        {
          id: 3,
          mentor_name: 'Дмитрий Иванов',
          topic: 'Подготовка к собеседованию',
          scheduled_time: '2024-02-20T14:00:00',
          duration: 60,
          price: 45,
          status: 'confirmed',
          meeting_link: 'https://meet.example.com/def456'
        }
      ] : [
        {
          id: 4,
          mentor_name: 'Елена Козлова',
          topic: 'Введение в Next.js',
          scheduled_time: '2024-01-25T16:00:00',
          duration: 60,
          price: 70,
          status: 'completed'
        },
        {
          id: 5,
          mentor_name: 'Алексей Николаев',
          topic: 'Docker и Kubernetes основы',
          scheduled_time: '2024-01-20T11:00:00',
          duration: 120,
          price: 110,
          status: 'completed'
        }
      ];
      
      setSessions(mockSessions);
      setLoading(false);
    }, 500);
  };

  const handleCancelSession = (sessionId: number) => {
    if (confirm('Вы уверены, что хотите отменить эту сессию?')) {
      // API запрос на отмену
      alert(`Сессия ${sessionId} отменена`);
    }
  };

  const getStatusBadge = (status: Session['status']) => {
    const badges = {
      pending: { text: 'Ожидает подтверждения', color: 'bg-yellow-100 text-yellow-800', icon: AlertCircle },
      confirmed: { text: 'Подтверждена', color: 'bg-green-100 text-green-800', icon: CheckCircle },
      completed: { text: 'Завершена', color: 'bg-blue-100 text-blue-800', icon: CheckCircle },
      cancelled: { text: 'Отменена', color: 'bg-red-100 text-red-800', icon: X }
    };
    
    const badge = badges[status];
    const Icon = badge.icon;
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}>
        <Icon className="h-4 w-4 mr-1" />
        {badge.text}
      </span>
    );
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    const options: Intl.DateTimeFormatOptions = { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    const timeOptions: Intl.DateTimeFormatOptions = { 
      hour: '2-digit', 
      minute: '2-digit' 
    };
    
    return {
      date: date.toLocaleDateString('ru-RU', options),
      time: date.toLocaleTimeString('ru-RU', timeOptions)
    };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="py-8">
        {/* Header */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Мои сессии</h1>
          <p className="mt-2 text-lg text-gray-600">
            Управляйте своими менторскими сессиями
          </p>
        </div>

        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('upcoming')}
                className={`${
                  activeTab === 'upcoming'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Предстоящие
                <span className={`ml-2 py-0.5 px-2.5 rounded-full text-xs ${
                  activeTab === 'upcoming' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                }`}>
                  {activeTab === 'upcoming' ? sessions.length : 0}
                </span>
              </button>
              <button
                onClick={() => setActiveTab('past')}
                className={`${
                  activeTab === 'past'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Прошедшие
                <span className={`ml-2 py-0.5 px-2.5 rounded-full text-xs ${
                  activeTab === 'past' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                }`}>
                  {activeTab === 'past' ? sessions.length : 0}
                </span>
              </button>
            </nav>
          </div>

          {/* Sessions List */}
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="h-12 w-12 bg-gray-300 rounded-full"></div>
                      <div className="flex-1">
                        <div className="h-4 bg-gray-300 rounded w-48 mb-2"></div>
                        <div className="h-3 bg-gray-300 rounded w-32"></div>
                      </div>
                    </div>
                    <div className="h-6 bg-gray-300 rounded w-24"></div>
                  </div>
                  <div className="h-3 bg-gray-300 rounded w-64"></div>
                </div>
              ))}
            </div>
          ) : sessions.length > 0 ? (
            <div className="space-y-4">
              {sessions.map((session) => {
                const { date, time } = formatDateTime(session.scheduled_time);
                
                return (
                  <div key={session.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                    <div className="p-6">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-start space-x-4 flex-1">
                          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full h-12 w-12 flex items-center justify-center flex-shrink-0">
                            <span className="text-lg font-bold text-white">
                              {session.mentor_name.split(' ').map(n => n[0]).join('')}
                            </span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {session.topic}
                            </h3>
                            <div className="flex items-center text-sm text-gray-600">
                              <User className="h-4 w-4 mr-1" />
                              <span>с {session.mentor_name}</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0 ml-4">
                          <p className="text-xl font-bold text-gray-900">
                            ${session.price}
                          </p>
                          <p className="text-sm text-gray-500">
                            {session.duration} минут
                          </p>
                        </div>
                      </div>

                      {/* Details */}
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-sm text-gray-700">
                          <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{date}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-700">
                          <Clock className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{time} ({session.duration} мин)</span>
                        </div>
                      </div>

                      {/* Status & Actions */}
                      <div className="flex items-center justify-between pt-4 border-t">
                        <div>
                          {getStatusBadge(session.status)}
                        </div>
                        
                        <div className="flex space-x-3">
                          {activeTab === 'upcoming' && session.status === 'confirmed' && session.meeting_link && (
                            <a
                              href={session.meeting_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                            >
                              <Video className="h-4 w-4 mr-2" />
                              Присоединиться
                            </a>
                          )}
                          
                          {activeTab === 'upcoming' && session.status !== 'cancelled' && (
                            <button
                              onClick={() => handleCancelSession(session.id)}
                              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                            >
                              <X className="h-4 w-4 mr-2" />
                              Отменить
                            </button>
                          )}
                          
                          {activeTab === 'past' && session.status === 'completed' && (
                            <button className="inline-flex items-center px-4 py-2 border border-blue-600 rounded-md shadow-sm text-sm font-medium text-blue-600 bg-white hover:bg-blue-50">
                              Оставить отзыв
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg shadow-md">
              <Calendar className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-lg font-medium text-gray-900">
                {activeTab === 'upcoming' ? 'Нет предстоящих сессий' : 'Нет прошедших сессий'}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {activeTab === 'upcoming' 
                  ? 'Забронируйте сессию с ментором, чтобы начать обучение'
                  : 'Здесь появятся завершённые сессии'}
              </p>
              {activeTab === 'upcoming' && (
                <div className="mt-6">
                  <a
                    href="/mentors"
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Найти ментора
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}