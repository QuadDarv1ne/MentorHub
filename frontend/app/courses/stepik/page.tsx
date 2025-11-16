"use client";
import React, { useState, useEffect } from 'react';
import StepikCourseCard from '@/components/StepikCourseCard';
import { Search, BarChart3, Users, Award, DollarSign, X } from 'lucide-react';

interface Course {
  id: string;
  title: string;
  description: string;
  stepikUrl: string;
  price: number;
  studentsCount: number;
  rating: number;
  category: string;
}

interface Filters {
  search: string;
  category: string;
  sort: string;
  price: string;
}

const allCourses: Course[] = [
  {
    id: '210134',
    title: 'Java полное руководство',
    description: 'Полный курс по языку программирования Java с нуля до профессионального уровня. Изучите основы, ООП, коллекции, многопоточность и многое другое.',
    stepikUrl: 'https://stepik.org/a/210134',
    price: 0,
    studentsCount: 150,
    rating: 4.8,
    category: 'Java'
  },
  {
    id: '178781',
    title: 'Python разработка с нуля',
    description: 'Практический курс по Python: от основ до создания реальных проектов. Включает работу с базами данных, веб-разработку и автоматизацию.',
    stepikUrl: 'https://stepik.org/a/178781',
    price: 0,
    studentsCount: 200,
    rating: 4.9,
    category: 'Python'
  },
  {
    id: '212445',
    title: 'Android разработка для начинающих',
    description: 'Создавайте мобильные приложения для Android. Курс охватывает основы разработки, работу с UI компонентами, базами данных и API.',
    stepikUrl: 'https://stepik.org/a/212445',
    price: 0,
    studentsCount: 120,
    rating: 4.7,
    category: 'Android'
  },
  {
    id: '252727',
    title: 'DevOps практики и инструменты',
    description: 'Изучите основные практики и инструменты DevOps: Docker, Kubernetes, CI/CD, мониторинг и автоматизацию.',
    stepikUrl: 'https://stepik.org/a/252727',
    price: 0,
    studentsCount: 80,
    rating: 4.6,
    category: 'DevOps'
  },
  {
    id: '252698',
    title: 'Базы данных и SQL',
    description: 'Комплексный курс по работе с базами данных: проектирование, SQL, оптимизация запросов, работа с PostgreSQL.',
    stepikUrl: 'https://stepik.org/a/252698',
    price: 0,
    studentsCount: 170,
    rating: 4.8,
    category: 'Базы данных'
  },
  {
    id: '238534',
    title: 'Frontend разработка',
    description: 'Современная frontend разработка: HTML, CSS, JavaScript, React. Создание адаптивных и интерактивных веб-приложений.',
    stepikUrl: 'https://stepik.org/a/238534',
    price: 0,
    studentsCount: 190,
    rating: 4.9,
    category: 'Frontend'
  }
];

export default function StepikCoursesPage() {
  const [courses, setCourses] = useState<Course[]>(allCourses);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    search: '',
    category: '',
    sort: 'popular',
    price: ''
  });

  useEffect(() => {
    applyFilters();
  }, [filters]);

  const applyFilters = () => {
    setLoading(true);
    
    let filtered = [...allCourses];

    // Фильтр по поиску
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(course => 
        course.title.toLowerCase().includes(searchLower) ||
        course.description.toLowerCase().includes(searchLower) ||
        course.category.toLowerCase().includes(searchLower)
      );
    }

    // Фильтр по категории
    if (filters.category) {
      filtered = filtered.filter(course => 
        course.category.toLowerCase() === filters.category.toLowerCase()
      );
    }

    // Фильтр по цене
    if (filters.price === 'free') {
      filtered = filtered.filter(course => course.price === 0);
    } else if (filters.price === 'paid') {
      filtered = filtered.filter(course => course.price > 0);
    }

    // Сортировка
    switch (filters.sort) {
      case 'popular':
        filtered.sort((a, b) => b.studentsCount - a.studentsCount);
        break;
      case 'rating':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      case 'newest':
        // По умолчанию порядок - сначала новые
        break;
    }

    setTimeout(() => {
      setCourses(filtered);
      setLoading(false);
    }, 300);
  };

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      sort: 'popular',
      price: ''
    });
  };

  const hasActiveFilters = filters.search || filters.category || filters.price || filters.sort !== 'popular';

  const stats = {
    totalCourses: allCourses.length,
    totalStudents: allCourses.reduce((sum, course) => sum + course.studentsCount, 0),
    averageRating: (allCourses.reduce((sum, course) => sum + course.rating, 0) / allCourses.length).toFixed(1),
    freeCourses: allCourses.filter(course => course.price === 0).length
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="py-8">
        {/* Header */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-4xl font-bold text-gray-900">
                Курсы на Stepik
              </h1>
              <p className="mt-2 text-lg text-gray-600">
                Курсы от преподавателя Дуплей Максима Игоревича
              </p>
            </div>
            <div className="mt-4 flex md:mt-0 md:ml-4">
              <a
                href="https://stepik.org/users/150943726/teach"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Профиль на Stepik
              </a>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-white overflow-hidden shadow-md rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BarChart3 className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Всего курсов
                      </dt>
                      <dd className="text-3xl font-semibold text-gray-900">
                        {stats.totalCourses}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow-md rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Users className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Всего учеников
                      </dt>
                      <dd className="text-3xl font-semibold text-gray-900">
                        {stats.totalStudents}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow-md rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Award className="h-8 w-8 text-yellow-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Средний рейтинг
                      </dt>
                      <dd className="text-3xl font-semibold text-gray-900">
                        {stats.averageRating}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow-md rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <DollarSign className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Бесплатных курсов
                      </dt>
                      <dd className="text-3xl font-semibold text-gray-900">
                        {stats.freeCourses}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
          <div className="bg-white shadow-md rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Поиск по курсам..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>

              {/* Category */}
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                aria-label="Категория курса"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">Все категории</option>
                <option value="java">Java</option>
                <option value="python">Python</option>
                <option value="android">Android</option>
                <option value="devops">DevOps</option>
                <option value="базы данных">Базы данных</option>
                <option value="frontend">Frontend</option>
              </select>

              {/* Sort */}
              <select
                value={filters.sort}
                onChange={(e) => handleFilterChange('sort', e.target.value)}
                aria-label="Сортировка"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="popular">По популярности</option>
                <option value="rating">По рейтингу</option>
                <option value="newest">Сначала новые</option>
              </select>

              {/* Price */}
              <select
                value={filters.price}
                onChange={(e) => handleFilterChange('price', e.target.value)}
                aria-label="Цена"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">Любая цена</option>
                <option value="free">Бесплатные</option>
                <option value="paid">Платные</option>
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

        {/* Course List */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {loading ? (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                  <div className="h-4 bg-gray-300 rounded w-3/4 mb-4"></div>
                  <div className="h-3 bg-gray-300 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded w-5/6"></div>
                </div>
              ))}
            </div>
          ) : courses.length > 0 ? (
            <>
              <div className="mb-4 text-sm text-gray-600">
                Найдено курсов: {courses.length}
              </div>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {courses.map(course => (
                  <StepikCourseCard key={course.id} {...course} />
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg shadow-md">
              <Search className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-lg font-medium text-gray-900">Курсы не найдены</h3>
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