'use client'

import Link from 'next/link'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <nav className="container-custom">
        <div className="flex items-center justify-between h-16">
          {/* Логотип */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">M</span>
              </div>
              <span className="text-xl font-bold text-gray-900">MentorHub</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/mentors" className="text-gray-700 hover:text-primary-600 transition-colors">
              Менторы
            </Link>
            <Link href="/courses" className="text-gray-700 hover:text-primary-600 transition-colors">
              Курсы
            </Link>
            <Link href="/sessions" className="text-gray-700 hover:text-primary-600 transition-colors">
              Сессии
            </Link>
            <Link href="/learning" className="text-gray-700 hover:text-primary-600 transition-colors">
              Обучение
            </Link>
            <Link href="/roadmap" className="text-gray-700 hover:text-primary-600 transition-colors">
              Роадмапы
            </Link>
          </div>

          {/* Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Link href="/login" className="text-gray-700 hover:text-primary-600 transition-colors">
              Войти
            </Link>
            <Link href="/register" className="btn-primary">
              Начать
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-md text-gray-700"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <div className="flex flex-col space-y-4">
              <Link href="/mentors" className="text-gray-700 hover:text-primary-600 transition-colors">
                Менторы
              </Link>
              <Link href="/courses" className="text-gray-700 hover:text-primary-600 transition-colors">
                Курсы
              </Link>
              <Link href="/sessions" className="text-gray-700 hover:text-primary-600 transition-colors">
                Сессии
              </Link>
              <Link href="/learning" className="text-gray-700 hover:text-primary-600 transition-colors">
                Обучение
              </Link>
              <Link href="/roadmap" className="text-gray-700 hover:text-primary-600 transition-colors">
                Роадмапы
              </Link>
              <div className="pt-4 border-t border-gray-200 flex flex-col space-y-2">
                <Link href="/login" className="text-gray-700 hover:text-primary-600 transition-colors">
                  Войти
                </Link>
                <Link href="/register" className="btn-primary text-center">
                  Начать
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}

