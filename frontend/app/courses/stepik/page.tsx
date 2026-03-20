"use client";
import React, { useState, useEffect, useCallback } from 'react';
import StepikCourseCard from '@/components/StepikCourseCard';
import { Search, BarChart3, Users, Award, DollarSign, X } from 'lucide-react';
import { getCourses, type StepikCourse } from '@/lib/api/stepik';

interface Course {
  id: string;
  title: string;
  description: string;
  stepikUrl: string;
  price: number;
  studentsCount: number;
  rating: number;
  category: string;
  imageUrl?: string;
  duration?: string;
  level?: 'beginner' | 'intermediate' | 'advanced';
  tags?: string[];
}

interface Filters {
  search: string;
  category: string;
  sort: string;
  price: string;
}

// Преобразование данных Stepik API в формат компонента
function mapStepikCourse(course: StepikCourse): Course {
  // Определяем категорию на основе языка или названия
  const categoryMap: Record<string, string> = {
    'python': 'Python',
    'java': 'Java',
    'android': 'Android',
    'web': 'Web Development',
    'frontend': 'Frontend',
    'backend': 'Backend',
    'devops': 'DevOps',
    'database': 'Базы данных',
    'sql': 'Базы данных',
  };

  const titleLower = course.title.toLowerCase();
  const languageLower = course.language?.toLowerCase() || '';
  
  let category = 'Другое';
  for (const [key, value] of Object.entries(categoryMap)) {
    if (titleLower.includes(key) || languageLower.includes(key)) {
      category = value;
      break;
    }
  }

  // Определяем уровень сложности
  let level: 'beginner' | 'intermediate' | 'advanced' = 'beginner';
  if (titleLower.includes('продвинут') || titleLower.includes('advanced')) {
    level = 'advanced';
  } else if (titleLower.includes('средн') || titleLower.includes('intermediate')) {
    level = 'intermediate';
  }

  return {
    id: String(course.id),
    title: course.title,
    description: course.summary || course.description || '',
    stepikUrl: `https://stepik.org/course/${course.id}`,
    price: course.price || 0,
    studentsCount: course.learners_count || 0,
    rating: course.rating || course.review_summary?.average || 0,
    category,
    imageUrl: course.cover || undefined,
    duration: course.duration ? `${course.duration} ч.` : undefined,
    level,
    tags: [],
  };
}

export default function StepikCoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [allCourses, setAllCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>({
    search: '',
    category: '',
    sort: 'popular',
    price: ''
  });

  // Загрузка курсов из Stepik API
  useEffect(() => {
    const loadCourses = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getCourses(1);
        const stepikCourses = response.courses || [];
        const mappedCourses = stepikCourses.map(mapStepikCourse);
        setAllCourses(mappedCourses);
        setCourses(mappedCourses);
      } catch (err) {
        setError('Не удалось загрузить курсы. Попробуйте позже.');
      } finally {
        setLoading(false);
      }
    };

    loadCourses();
  }, []);

  const applyFilters = useCallback(() => {
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

    setCourses(filtered);
    setLoading(false);
  }, [allCourses, filters]);

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Применяем фильтры при их изменении
  useEffect(() => {
    if (allCourses.length > 0) {
      applyFilters();
    }
  }, [filters, allCourses, applyFilters]);

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      sort: 'popular',
      price: ''
    });
  };

  const hasActiveFilters = filters.search || filters.category || filters.price || filters.sort !== 'popular';

  // Динамическая статистика на основе загруженных курсов
  const stats = {
    totalCourses: allCourses.length,
    totalStudents: allCourses.reduce((sum, course) => sum + (course.studentsCount || 0), 0),
    averageRating: allCourses.length > 0 
      ? (allCourses.reduce((sum, course) => sum + (course.rating || 0), 0) / allCourses.length).toFixed(1)
      : '0.0',
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
          {error ? (
            <div className="text-center py-12 bg-white rounded-lg shadow-md">
              <Search className="mx-auto h-12 w-12 text-red-400" />
              <h3 className="mt-2 text-lg font-medium text-gray-900">{error}</h3>
              <p className="mt-1 text-sm text-gray-500">Проверьте подключение к интернету или попробуйте позже</p>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Обновить страницу
              </button>
            </div>
          ) : loading ? (
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