"use client";
import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Star, MapPin, Briefcase, Calendar, Clock, DollarSign, Award, MessageCircle } from 'lucide-react';

interface Mentor {
  id: number;
  full_name: string;
  email: string;
  bio?: string;
  location?: string;
  occupation?: string;
  hourly_rate?: number;
  experience_years?: number;
  specializations?: string[];
  rating?: number;
  total_sessions?: number;
}

export default function MentorDetailPage() {
  const params = useParams();
  const [mentor, setMentor] = useState<Mentor | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [bookingMessage, setBookingMessage] = useState('');

  useEffect(() => {
    // Имитация загрузки данных ментора
    setTimeout(() => {
      setMentor({
        id: Number(params.id),
        full_name: 'Иван Петров',
        email: 'ivan.petrov@example.com',
        bio: 'Опытный разработчик с более чем 10-летним стажем в веб-разработке. Специализируюсь на React, TypeScript и архитектуре фронтенд-приложений. Помогаю разработчикам расти профессионально через менторство и code review.',
        location: 'Москва, Россия',
        occupation: 'Senior Frontend Developer',
        hourly_rate: 50,
        experience_years: 10,
        specializations: ['React', 'TypeScript', 'Next.js', 'Node.js', 'PostgreSQL'],
        rating: 4.8,
        total_sessions: 127
      });
      setLoading(false);
    }, 500);
  }, [params.id]);

  const handleBooking = async () => {
    if (!selectedDate || !selectedTime) {
      alert('Пожалуйста, выберите дату и время');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      window.location.href = '/auth/login';
      return;
    }

    // Здесь будет реальный API запрос
    alert(`Запрос на бронирование отправлен!\nДата: ${selectedDate}\nВремя: ${selectedTime}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!mentor) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Ментор не найден</h2>
          <a href="/mentors" className="text-blue-600 hover:underline">Вернуться к списку</a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Header */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-700 h-24"></div>
              <div className="px-6 pb-6">
                <div className="flex items-start -mt-12">
                  <div className="bg-white rounded-full p-1 shadow-lg">
                    <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full h-24 w-24 flex items-center justify-center">
                      <span className="text-3xl font-bold text-white">
                        {mentor.full_name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                  </div>
                  <div className="ml-6 mt-14 flex-1">
                    <h1 className="text-3xl font-bold text-gray-900">{mentor.full_name}</h1>
                    <p className="text-lg text-gray-600 mt-1">{mentor.occupation}</p>
                    
                    <div className="flex items-center mt-3 gap-4">
                      <div className="flex items-center">
                        <Star className="h-5 w-5 text-yellow-400 fill-current" />
                        <span className="ml-1 text-sm font-medium text-gray-900">{mentor.rating}</span>
                        <span className="ml-1 text-sm text-gray-500">({mentor.total_sessions} сессий)</span>
                      </div>
                      
                      {mentor.location && (
                        <div className="flex items-center text-sm text-gray-500">
                          <MapPin className="h-4 w-4 mr-1" />
                          {mentor.location}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* About */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">О менторе</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{mentor.bio}</p>
            </div>

            {/* Experience & Skills */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Опыт и навыки</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="flex items-start">
                  <Briefcase className="h-6 w-6 text-blue-600 mt-0.5 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Опыт работы</p>
                    <p className="text-lg font-semibold text-gray-900">{mentor.experience_years}+ лет</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <Award className="h-6 w-6 text-green-600 mt-0.5 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Проведено сессий</p>
                    <p className="text-lg font-semibold text-gray-900">{mentor.total_sessions}</p>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">Специализации</p>
                <div className="flex flex-wrap gap-2">
                  {mentor.specializations?.map((skill, idx) => (
                    <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Reviews */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Отзывы</h2>
              <div className="space-y-4">
                <div className="border-b pb-4">
                  <div className="flex items-center mb-2">
                    <div className="flex items-center">
                      {[1,2,3,4,5].map(i => (
                        <Star key={i} className="h-4 w-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                    <span className="ml-3 text-sm font-medium text-gray-900">Анна Смирнова</span>
                    <span className="ml-2 text-sm text-gray-500">• 2 недели назад</span>
                  </div>
                  <p className="text-gray-700">Отличный ментор! Помог разобраться с архитектурой React-приложения. Очень понятно объясняет сложные концепции.</p>
                </div>
                
                <div className="border-b pb-4">
                  <div className="flex items-center mb-2">
                    <div className="flex items-center">
                      {[1,2,3,4].map(i => (
                        <Star key={i} className="h-4 w-4 text-yellow-400 fill-current" />
                      ))}
                      <Star className="h-4 w-4 text-gray-300" />
                    </div>
                    <span className="ml-3 text-sm font-medium text-gray-900">Дмитрий Иванов</span>
                    <span className="ml-2 text-sm text-gray-500">• месяц назад</span>
                  </div>
                  <p className="text-gray-700">Профессиональный подход, качественное code review. Рекомендую!</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Booking Card */}
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <DollarSign className="h-6 w-6 text-green-600" />
                  <span className="ml-2 text-2xl font-bold text-gray-900">${mentor.hourly_rate}</span>
                  <span className="ml-1 text-gray-500">/час</span>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="inline h-4 w-4 mr-1" />
                    Выберите дату
                  </label>
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Clock className="inline h-4 w-4 mr-1" />
                    Выберите время
                  </label>
                  <select
                    value={selectedTime}
                    onChange={(e) => setSelectedTime(e.target.value)}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">Выберите время</option>
                    <option value="09:00">09:00</option>
                    <option value="10:00">10:00</option>
                    <option value="11:00">11:00</option>
                    <option value="14:00">14:00</option>
                    <option value="15:00">15:00</option>
                    <option value="16:00">16:00</option>
                    <option value="17:00">17:00</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <MessageCircle className="inline h-4 w-4 mr-1" />
                    Сообщение (опционально)
                  </label>
                  <textarea
                    value={bookingMessage}
                    onChange={(e) => setBookingMessage(e.target.value)}
                    rows={3}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="Опишите, что вы хотели бы обсудить..."
                  />
                </div>

                <button
                  onClick={handleBooking}
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Забронировать сессию
                </button>

                <p className="text-xs text-gray-500 text-center">
                  Бронирование бесплатно. Оплата после подтверждения.
                </p>
              </div>
            </div>

            {/* Contact Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Связаться</h3>
              <button className="w-full flex items-center justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <MessageCircle className="h-4 w-4 mr-2" />
                Отправить сообщение
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
