'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Menu, X, User, LogOut } from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userName, setUserName] = useState('')
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    setIsAuthenticated(!!token)
    
    if (token) {
      // Попытка получить имя пользователя из localStorage или API
      const storedUser = localStorage.getItem('user_name')
      if (storedUser) {
        setUserName(storedUser)
      }
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_name')
    setIsAuthenticated(false)
    setUserName('')
    router.push('/')
  }

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
            <div className="relative group">
              <button 
                id="courses-menu"
                aria-haspopup="true"
                aria-expanded="false"
                className="text-gray-700 hover:text-primary-600 transition-colors inline-flex items-center group"
              >
                <span>Курсы</span>
                <svg className="ml-2 h-5 w-5 text-gray-400 group-hover:text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div className="absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="courses-menu">
                  <Link href="/courses" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
                    Все курсы
                  </Link>
                  <Link href="/courses/stepik" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
                    Курсы на Stepik
                  </Link>
                </div>
              </div>
            </div>
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

          {/* Auth Section */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link 
                  href="/dashboard" 
                  className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors"
                >
                  <User size={20} />
                  <span>{userName || 'Профиль'}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 text-gray-700 hover:text-red-600 transition-colors"
                  aria-label="Выйти"
                >
                  <LogOut size={20} />
                  <span>Выйти</span>
                </button>
              </>
            ) : (
              <>
                <Link href="/auth/login" className="text-gray-700 hover:text-primary-600 transition-colors">
                  Войти
                </Link>
                <Link href="/auth/register" className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                  Начать
                </Link>
              </>
            )}
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
                {isAuthenticated ? (
                  <>
                    <Link href="/dashboard" className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors">
                      <User size={20} />
                      <span>{userName || 'Профиль'}</span>
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-2 text-gray-700 hover:text-red-600 transition-colors"
                      aria-label="Выйти"
                    >
                      <LogOut size={20} />
                      <span>Выйти</span>
                    </button>
                  </>
                ) : (
                  <>
                    <Link href="/auth/login" className="text-gray-700 hover:text-primary-600 transition-colors">
                      Войти
                    </Link>
                    <Link href="/auth/register" className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 text-center">
                      Начать
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}

