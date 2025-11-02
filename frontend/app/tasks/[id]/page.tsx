import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Разбор задач | MentorHub',
  description: 'Практические задания и их решения на платформе MentorHub'
}

export default function TaskPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="py-10">
        <header>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold leading-tight text-gray-900">Задача #12</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Создание компонента ToDo • React для начинающих
                </p>
              </div>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                В процессе
              </span>
            </div>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div className="px-4 py-8 sm:px-0">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Описание задачи */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="p-6">
                      <h2 className="text-lg font-medium text-gray-900 mb-4">Описание задачи</h2>
                      <div className="prose max-w-none">
                        <p>
                          Создайте компонент ToDo с использованием React, который позволяет:
                        </p>
                        <ul>
                          <li>Добавлять новые задачи</li>
                          <li>Отмечать задачи как выполненные</li>
                          <li>Удалять задачи</li>
                          <li>Фильтровать задачи (все/активные/выполненные)</li>
                        </ul>
                        <h3>Требования:</h3>
                        <ul>
                          <li>Использовать функциональные компоненты</li>
                          <li>Использовать хуки useState и useEffect</li>
                          <li>Реализовать локальное хранение задач</li>
                          <li>Добавить базовую стилизацию</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Редактор кода */}
                  <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="p-6">
                      <h2 className="text-lg font-medium text-gray-900 mb-4">Ваше решение</h2>
                      <div className="bg-gray-800 rounded-lg p-4">
                        <pre className="text-gray-100 font-mono text-sm">
                          {`import React, { useState, useEffect } from 'react';

function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');
  
  // Ваш код здесь...
  
  return (
    <div>
      {/* Ваш JSX код здесь... */}
    </div>
  );
}`}
                        </pre>
                      </div>
                      <div className="mt-4 flex justify-end space-x-3">
                        <button className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                          Сохранить
                        </button>
                        <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                          Отправить на проверку
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Сайдбар */}
                <div className="space-y-6">
                  {/* Прогресс */}
                  <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="p-6">
                      <h2 className="text-lg font-medium text-gray-900 mb-4">Прогресс</h2>
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between text-sm text-gray-600 mb-1">
                            <span>Выполнено тестов</span>
                            <span>0/5</span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full">
                            <div className="h-2 bg-indigo-600 rounded-full w-0"></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm text-gray-600 mb-1">
                            <span>Время на задачу</span>
                            <span>45:00</span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full">
                            <div className="h-2 bg-indigo-600 rounded-full w-1/2"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Подсказки */}
                  <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="p-6">
                      <h2 className="text-lg font-medium text-gray-900 mb-4">Подсказки</h2>
                      <div className="space-y-4">
                        <div className="border-l-4 border-yellow-400 bg-yellow-50 p-4">
                          <div className="flex">
                            <div className="ml-3">
                              <p className="text-sm text-yellow-700">
                                Для хранения задач используйте localStorage
                              </p>
                            </div>
                          </div>
                        </div>
                        <button className="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                          Показать еще подсказку (2/3)
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Помощь ментора */}
                  <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="p-6">
                      <h2 className="text-lg font-medium text-gray-900 mb-4">Помощь ментора</h2>
                      <p className="text-sm text-gray-500 mb-4">
                        Застряли? Получите персональную консультацию по этой задаче
                      </p>
                      <button className="w-full bg-indigo-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-indigo-700">
                        Запросить помощь
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}