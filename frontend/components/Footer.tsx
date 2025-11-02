'use client'

import Link from 'next/link'
import { Github, Mail, Send } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container-custom py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* О проекте */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">MentorHub</h3>
            <p className="text-sm text-gray-400 mb-4">
              Платформа для профессионального менторства и карьерного развития в IT
            </p>
            <div className="flex space-x-4">
              <a href="https://github.com" className="text-gray-400 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="mailto:support@mentorhub.com" className="text-gray-400 hover:text-white transition-colors">
                <Mail className="w-5 h-5" />
              </a>
              <a href="https://t.me/mentorhub" className="text-gray-400 hover:text-white transition-colors">
                <Send className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Обучение */}
          <div>
            <h4 className="text-white font-semibold mb-4">Обучение</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/roadmaps" className="hover:text-white transition-colors">
                  Роадмапы
                </Link>
              </li>
              <li>
                <Link href="/questions" className="hover:text-white transition-colors">
                  Топ вопросов
                </Link>
              </li>
              <li>
                <Link href="/questions" className="hover:text-white transition-colors">
                  База вопросов
                </Link>
              </li>
            </ul>
          </div>

          {/* Собеседование */}
          <div>
            <h4 className="text-white font-semibold mb-4">Собеседование</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/interview" className="hover:text-white transition-colors">
                  Тренажёр
                </Link>
              </li>
              <li>
                <Link href="/coding" className="hover:text-white transition-colors">
                  Лайв кодинг
                </Link>
              </li>
            </ul>
          </div>

          {/* Поддержка */}
          <div>
            <h4 className="text-white font-semibold mb-4">Поддержка</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/profile" className="hover:text-white transition-colors">
                  Профиль
                </Link>
              </li>
              <li>
                <a href="https://t.me/support" className="hover:text-white transition-colors">
                  Поддержка (Telegram)
                </a>
              </li>
              <li>
                <Link href="/contact" className="hover:text-white transition-colors">
                  Связаться с нами
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-gray-400">
            © 2025 MentorHub. Все права защищены.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link href="/legal" className="text-sm text-gray-400 hover:text-white transition-colors">
              Правовая информация
            </Link>
            <Link href="/offer" className="text-sm text-gray-400 hover:text-white transition-colors">
              Оферта
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}