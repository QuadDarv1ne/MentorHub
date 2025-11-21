'use client'

import Link from 'next/link'
import { Home, Search, ArrowLeft, Mail, BookOpen, Users } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        {/* 404 Animation */}
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 animate-pulse">
            404
          </h1>
          <div className="mt-4 relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-32 h-32 bg-indigo-100 rounded-full opacity-20 animate-ping"></div>
            </div>
            <p className="relative text-2xl font-semibold text-gray-800">
              Страница не найдена
            </p>
          </div>
        </div>

        {/* Description */}
        <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
          К сожалению, страница, которую вы ищете, не существует или была перемещена.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <Link
            href="/"
            className="inline-flex items-center justify-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            <Home className="mr-2" size={20} />
            На главную
          </Link>
          
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 rounded-lg shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft className="mr-2" size={20} />
            Назад
          </Link>
        </div>

        {/* Quick Links */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Возможно, вы искали:
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link
              href="/search"
              className="flex items-center p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-all group"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
                <Search className="text-indigo-600" size={24} />
              </div>
              <div className="ml-4 text-left">
                <p className="text-sm font-medium text-gray-900">Поиск</p>
                <p className="text-xs text-gray-500">Найдите нужный курс</p>
              </div>
            </Link>

            <Link
              href="/mentors"
              className="flex items-center p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-all group"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                <Users className="text-purple-600" size={24} />
              </div>
              <div className="ml-4 text-left">
                <p className="text-sm font-medium text-gray-900">Менторы</p>
                <p className="text-xs text-gray-500">Просмотр менторов</p>
              </div>
            </Link>

            <Link
              href="/courses"
              className="flex items-center p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-all group"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
                <BookOpen className="text-green-600" size={24} />
              </div>
              <div className="ml-4 text-left">
                <p className="text-sm font-medium text-gray-900">Курсы</p>
                <p className="text-xs text-gray-500">Каталог курсов</p>
              </div>
            </Link>

            <Link
              href="/contact"
              className="flex items-center p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-all group"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                <Mail className="text-blue-600" size={24} />
              </div>
              <div className="ml-4 text-left">
                <p className="text-sm font-medium text-gray-900">Контакты</p>
                <p className="text-xs text-gray-500">Свяжитесь с нами</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Help Text */}
        <p className="mt-8 text-sm text-gray-500">
          Если проблема повторяется, пожалуйста,{' '}
          <Link href="/contact" className="text-indigo-600 hover:text-indigo-500 font-medium">
            свяжитесь с поддержкой
          </Link>
        </p>
      </div>
    </div>
  )
}
