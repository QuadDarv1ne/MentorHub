import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Менторы | MentorHub',
  description: 'Найдите своего ментора на платформе MentorHub'
}

export default function MentorsPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="py-10">
        <header>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold leading-tight text-gray-900">Найти ментора</h1>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div className="px-4 py-8 sm:px-0">
              {/* Фильтры */}
              <div className="bg-white shadow rounded-lg mb-6 p-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <input
                    type="text"
                    placeholder="Поиск по навыкам..."
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  <select className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                    <option value="">Специализация</option>
                    <option value="frontend">Frontend</option>
                    <option value="backend">Backend</option>
                    <option value="fullstack">Fullstack</option>
                  </select>
                  <select className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                    <option value="">Опыт работы</option>
                    <option value="1-3">1-3 года</option>
                    <option value="3-5">3-5 лет</option>
                    <option value="5+">5+ лет</option>
                  </select>
                  <select className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                    <option value="">Цена за час</option>
                    <option value="0-25">$0-25</option>
                    <option value="25-50">$25-50</option>
                    <option value="50+">$50+</option>
                  </select>
                </div>
              </div>

              {/* Список менторов */}
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {/* Заглушка для карточки ментора */}
                <div className="bg-white overflow-hidden shadow rounded-lg divide-y divide-gray-200">
                  <div className="px-4 py-5 sm:px-6">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-gray-300"></div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">Имя Ментора</p>
                        <p className="text-sm text-gray-500">Senior Frontend Developer</p>
                      </div>
                    </div>
                  </div>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="text-sm">
                      <p className="text-gray-500">5 лет опыта • React, TypeScript, Node.js</p>
                      <p className="mt-2 text-gray-900">$50/час</p>
                    </div>
                  </div>
                  <div className="px-4 py-4 sm:px-6">
                    <button className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                      Забронировать сессию
                    </button>
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