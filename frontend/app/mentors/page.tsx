"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Search, Star, MapPin, DollarSign, Filter, X } from 'lucide-react';

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

interface Filters {
  search: string;
  specialization: string;
  experience: string;
  priceRange: string;
}

export default function MentorsPage() {
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Filters>({
    search: '',
    specialization: '',
    experience: '',
    priceRange: ''
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages] = useState(3);

  useEffect(() => {
    fetchMentors();
  }, [filters, currentPage]);

  const fetchMentors = async () => {
    setLoading(true);
    
    // Имитация API запроса
    setTimeout(() => {
      const mockMentors: Mentor[] = [
        {
          id: 1,
          full_name: 'Иван Петров',
          email: 'ivan@example.com',
          bio: 'Опытный разработчик с фокусом на React и TypeScript',
          location: 'Москва, Россия',
          occupation: 'Senior Frontend Developer',
          hourly_rate: 50,
          experience_years: 10,
          specializations: ['React', 'TypeScript', 'Next.js'],
          rating: 4.8,
          total_sessions: 127
        },
        {
          id: 2,
          full_name: 'Анна Смирнова',
          email: 'anna@example.com',
          bio: 'Специализируюсь на backend-разработке и микросервисах',
          location: 'Санкт-Петербург, Россия',
          occupation: 'Senior Backend Developer',
          hourly_rate: 60,
          experience_years: 8,
          specializations: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
          rating: 4.9,
          total_sessions: 95
        },
        {
          id: 3,
          full_name: 'Дмитрий Иванов',
          email: 'dmitry@example.com',
          bio: 'Fullstack разработчик с опытом в стартапах',
          location: 'Новосибирск, Россия',
          occupation: 'Fullstack Developer',
          hourly_rate: 45,
          experience_years: 6,
          specializations: ['React', 'Node.js', 'MongoDB'],
          rating: 4.7,
          total_sessions: 78
        },
        {
          id: 4,
          full_name: 'Елена Козлова',
          email: 'elena@example.com',
          bio: 'Эксперт в архитектуре фронтенд-приложений',
          location: 'Казань, Россия',
          occupation: 'Lead Frontend Engineer',
          hourly_rate: 70,
          experience_years: 12,
          specializations: ['React', 'Vue.js', 'Angular', 'TypeScript'],
          rating: 5.0,
          total_sessions: 156
        },
        {
          id: 5,
          full_name: 'Алексей Николаев',
          email: 'alex@example.com',
          bio: 'DevOps инженер с фокусом на Kubernetes',
          location: 'Екатеринбург, Россия',
          occupation: 'Senior DevOps Engineer',
          hourly_rate: 55,
          experience_years: 9,
          specializations: ['Kubernetes', 'Docker', 'AWS', 'CI/CD'],
          rating: 4.6,
          total_sessions: 64
        },
        {
          id: 6,
          full_name: 'Мария Волкова',
          email: 'maria@example.com',
          bio: 'Data Science и машинное обучение',
          location: 'Москва, Россия',
          occupation: 'Senior Data Scientist',
          hourly_rate: 65,
          experience_years: 7,
          specializations: ['Python', 'TensorFlow', 'PyTorch', 'SQL'],
          rating: 4.8,
          total_sessions: 89
        }
      ];
      
      setMentors(mockMentors);
      setLoading(false);
    }, 500);
  };

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      specialization: '',
      experience: '',
      priceRange: ''
    });
    setCurrentPage(1);
  };

  const hasActiveFilters = Object.values(filters).some(v => v !== '');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="py-8">
        {/* Header */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Найти ментора</h1>
          <p className="mt-2 text-lg text-gray-600">
            Найдите опытного специалиста для достижения ваших целей
          </p>
        </div>

        {/* Filters */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
          <div className="bg-white shadow-md rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {/* Search */}
              <div className="lg:col-span-2 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Поиск по навыкам или имени..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>

              {/* Specialization */}
              <select
                value={filters.specialization}
                onChange={(e) => handleFilterChange('specialization', e.target.value)}
                aria-label="Специализация"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">Все специализации</option>
                <option value="frontend">Frontend</option>
                <option value="backend">Backend</option>
                <option value="fullstack">Fullstack</option>
                <option value="devops">DevOps</option>
                <option value="data">Data Science</option>
              </select>

              {/* Experience */}
              <select
                value={filters.experience}
                onChange={(e) => handleFilterChange('experience', e.target.value)}
                aria-label="Опыт работы"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">Любой опыт</option>
                <option value="1-3">1-3 года</option>
                <option value="3-5">3-5 лет</option>
                <option value="5-10">5-10 лет</option>
                <option value="10+">10+ лет</option>
              </select>

              {/* Price Range */}
              <select
                value={filters.priceRange}
                onChange={(e) => handleFilterChange('priceRange', e.target.value)}
                aria-label="Цена за час"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">Любая цена</option>
                <option value="0-30">$0-30/час</option>
                <option value="30-50">$30-50/час</option>
                <option value="50-70">$50-70/час</option>
                <option value="70+">$70+/час</option>
              </select>
            </div>

            {hasActiveFilters && (
              <div className="mt-4 flex items-center">
                <button
                  onClick={clearFilters}
                  className="flex items-center text-sm text-blue-600 hover:text-blue-700"
                >
                  <X className="h-4 w-4 mr-1" />
                  Сбросить фильтры
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {loading ? (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                  <div className="flex items-center mb-4">
                    <div className="h-16 w-16 bg-gray-300 rounded-full"></div>
                    <div className="ml-4 flex-1">
                      <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                    </div>
                  </div>
                  <div className="h-3 bg-gray-300 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded w-5/6"></div>
                </div>
              ))}
            </div>
          ) : mentors.length > 0 ? (
            <>
              <div className="mb-4 text-sm text-gray-600">
                Найдено {mentors.length} менторов
              </div>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {mentors.map((mentor) => (
                  <Link
                    key={mentor.id}
                    href={`/mentors/${mentor.id}`}
                    className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-200 overflow-hidden"
                  >
                    <div className="p-6">
                      {/* Avatar & Basic Info */}
                      <div className="flex items-start mb-4">
                        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full h-16 w-16 flex items-center justify-center flex-shrink-0">
                          <span className="text-2xl font-bold text-white">
                            {mentor.full_name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div className="ml-4 flex-1 min-w-0">
                          <h3 className="text-lg font-semibold text-gray-900 truncate">
                            {mentor.full_name}
                          </h3>
                          <p className="text-sm text-gray-600 truncate">{mentor.occupation}</p>
                          
                          <div className="flex items-center mt-1">
                            <Star className="h-4 w-4 text-yellow-400 fill-current" />
                            <span className="ml-1 text-sm font-medium text-gray-900">{mentor.rating}</span>
                            <span className="ml-1 text-sm text-gray-500">({mentor.total_sessions})</span>
                          </div>
                        </div>
                      </div>

                      {/* Bio */}
                      <p className="text-sm text-gray-700 mb-4 line-clamp-2">{mentor.bio}</p>

                      {/* Skills */}
                      <div className="flex flex-wrap gap-2 mb-4">
                        {mentor.specializations?.slice(0, 3).map((skill, idx) => (
                          <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {skill}
                          </span>
                        ))}
                        {mentor.specializations && mentor.specializations.length > 3 && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                            +{mentor.specializations.length - 3}
                          </span>
                        )}
                      </div>

                      {/* Footer */}
                      <div className="flex items-center justify-between pt-4 border-t">
                        <div className="flex items-center text-sm text-gray-500">
                          <MapPin className="h-4 w-4 mr-1" />
                          <span className="truncate">{mentor.location}</span>
                        </div>
                        <div className="flex items-center">
                          <DollarSign className="h-5 w-5 text-green-600" />
                          <span className="text-lg font-bold text-gray-900">{mentor.hourly_rate}</span>
                          <span className="text-sm text-gray-500">/час</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8 flex justify-center">
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-4 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Назад
                    </button>
                    
                    {[...Array(totalPages)].map((_, i) => (
                      <button
                        key={i + 1}
                        onClick={() => setCurrentPage(i + 1)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          currentPage === i + 1
                            ? 'z-10 bg-blue-600 border-blue-600 text-white'
                            : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        {i + 1}
                      </button>
                    ))}
                    
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-4 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Вперёд
                    </button>
                  </nav>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <Filter className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-lg font-medium text-gray-900">Менторы не найдены</h3>
              <p className="mt-1 text-sm text-gray-500">Попробуйте изменить параметры поиска</p>
              <button
                onClick={clearFilters}
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Сбросить фильтры
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}