'use client'

import Link from 'next/link'
import { Home, Search, FileQuestion } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center px-4">
      <div className="max-w-lg w-full text-center">
        <div className="mb-8">
          <div className="relative inline-block">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-32 h-32 bg-indigo-100 rounded-full opacity-20 animate-pulse"></div>
            </div>
            <div className="relative w-32 h-32 bg-indigo-100 rounded-full flex items-center justify-center mx-auto">
              <FileQuestion className="text-indigo-600" size={64} />
            </div>
          </div>
          <h1 className="mt-6 text-4xl font-bold text-gray-900">
            Страница не найдена
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Запрашиваемая страница не существует или была перемещена
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 mb-8">
          <div className="text-left">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Возможные причины:
            </h3>
            <ul className="text-sm text-gray-600 space-y-2">
              <li className="flex items-start">
                <span className="text-indigo-600 mr-2">•</span>
                Неправильный адрес страницы
              </li>
              <li className="flex items-start">
                <span className="text-indigo-600 mr-2">•</span>
                Страница была удалена
              </li>
              <li className="flex items-start">
                <span className="text-indigo-600 mr-2">•</span>
                У вас нет доступа к этой странице
              </li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="inline-flex items-center justify-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transition-all"
          >
            <Home className="mr-2" size={20} />
            На главную
          </Link>
          
          <Link
            href="/search"
            className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 rounded-lg shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 transition-all"
          >
            <Search className="mr-2" size={20} />
            Поиск по сайту
          </Link>
        </div>

        <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Совет:</strong> Проверьте адрес в адресной строке или воспользуйтесь поиском
          </p>
        </div>
      </div>
    </div>
  )
}