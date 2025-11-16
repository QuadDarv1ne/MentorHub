import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Обучение | MentorHub',
  description: 'Ваш персональный путь обучения на платформе MentorHub'
}

export default function LearningPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="py-10">
        <header>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold leading-tight text-gray-900">Мое обучение</h1>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div className="px-4 py-8 sm:px-0">
              {/* Прогресс */}
              <div className="bg-white shadow rounded-lg p-6 mb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Общий прогресс</h2>
                <div className="relative pt-1">
                  <div className="flex mb-2 items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-200">
                        В процессе
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-semibold inline-block text-indigo-600">
                        65%
                      </span>
                    </div>
                  </div>
                  <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-indigo-200">
                    <div className="w-2/3 shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-600"></div>
                  </div>
                </div>
              </div>

              {/* Активные курсы */}
              <div className="mb-8">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Активные курсы</h2>
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {/* Карточка курса */}
                  <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="p-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        React для начинающих
                      </h3>
                      <div className="flex items-center text-sm text-gray-500 mb-4">
                        <svg className="h-5 w-5 mr-2" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        8 из 12 уроков
                      </div>
                      <div className="relative pt-1">
                        <progress max="100" value="66" className="w-full h-2 rounded">
                          66%
                        </progress>
                      </div>
                      <button className="w-full bg-indigo-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-indigo-700">
                        Продолжить
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Задания */}
              <div>
                <h2 className="text-lg font-medium text-gray-900 mb-4">Текущие задания</h2>
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                  <ul className="divide-y divide-gray-200">
                    <li>
                      <a href="/tasks/12" className="block hover:bg-gray-50">
                        <div className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <div className="flex-shrink-0">
                                <span className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center">
                                  <span className="text-indigo-600 font-medium">1</span>
                                </span>
                              </div>
                              <div className="ml-4">
                                <p className="text-sm font-medium text-indigo-600">
                                  Создание компонента ToDo
                                </p>
                                <p className="text-sm text-gray-500">
                                  React для начинающих • Урок 8
                                </p>
                              </div>
                            </div>
                            <div className="ml-2 flex-shrink-0">
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                                В процессе
                              </span>
                            </div>
                          </div>
                        </div>
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}