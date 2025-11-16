import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Курсы | MentorHub',
  description: 'Изучайте программирование с помощью курсов на платформе MentorHub'
}

export default function CoursesPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="py-10">
        <header>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold leading-tight text-gray-900">Курсы</h1>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div className="px-4 py-8 sm:px-0">
              {/* Фильтры */}
              <div className="bg-white shadow rounded-lg mb-6 p-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <input
                    type="text"
                    placeholder="Поиск курсов..."
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  <select 
                    id="category"
                    name="category"
                    aria-label="Категория курса"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="">Все категории</option>
                    <option value="frontend">Frontend разработка</option>
                    <option value="backend">Backend разработка</option>
                    <option value="mobile">Мобильная разработка</option>
                  </select>
                  <select
                    id="level"
                    name="level"
                    aria-label="Уровень сложности"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="">Все уровни</option>
                    <option value="beginner">Начинающий</option>
                    <option value="intermediate">Средний</option>
                    <option value="advanced">Продвинутый</option>
                  </select>
                </div>
              </div>

              {/* Список курсов */}
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {/* Карточка курса */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="aspect-w-16 aspect-h-9">
                    <div className="w-full h-48 bg-gray-300"></div>
                  </div>
                  <div className="p-6">
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">
                        Frontend
                      </span>
                      <span className="px-2 py-1 text-xs font-semibold text-blue-800 bg-blue-100 rounded-full">
                        Начальный
                      </span>
                    </div>
                    <h3 className="mt-4 text-lg font-medium text-gray-900">
                      Основы React разработки
                    </h3>
                    <p className="mt-2 text-sm text-gray-500">
                      Изучите основы React, создавая реальные проекты под руководством опытных менторов.
                    </p>
                    <div className="mt-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="flex items-center">
                            <svg className="h-4 w-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            <span className="ml-1 text-sm text-gray-500">4.8</span>
                          </div>
                          <span className="text-sm text-gray-500">•</span>
                          <span className="text-sm text-gray-500">2,345 учеников</span>
                        </div>
                        <span className="text-lg font-medium text-gray-900">4999 ₽</span>
                      </div>
                      <button className="mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Подробнее
                      </button>
                    </div>
                  </div>
                </div>

                {/* Повторите карточку для демонстрации */}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}