'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Menu, X, User, LogOut, MessageSquare } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { NotificationCenter } from './NotificationCenter'
import { NavMenu, MobileNavMenu } from './navigation/NavMenu'

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

          {/* Компактная навигация (desktop) */}
          <div className="hidden md:flex items-center gap-6">
            <Link href="/mentors" className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors">Менторы</Link>
            <Link href="/courses" className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors">Курсы</Link>
            <Link href="/sessions" className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors">Сессии</Link>
            <Link href="/messages" className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors">Сообщения</Link>
            <NavMenu />
          </div>

          {/* Auth Section */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link 
                  href="/messages" 
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative"
                  title="Сообщения"
                  aria-label="Сообщения"
                >
                  <MessageSquare className="w-6 h-6 text-gray-600" />
                </Link>
                <NotificationCenter />
                <Link 
                  href="/profile" 
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
            <MobileNavMenu />
            <div className="mt-4 pt-4 border-t border-gray-200 flex flex-col space-y-2">
              {isAuthenticated ? (
                <>
                  <Link href="/profile" className="flex items-center space-x-2 text-gray-700 hover:text-indigo-600 transition-colors">
                    <User size={20} />
                    <span>{userName || 'Профиль'}</span>
                  </Link>
                  <Link href="/notifications" className="text-gray-700 hover:text-indigo-600 transition-colors">
                    Уведомления
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
                  <Link href="/auth/login" className="text-gray-700 hover:text-indigo-600 transition-colors">
                    Войти
                  </Link>
                  <Link href="/auth/register" className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 text-center">
                    Начать
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}
