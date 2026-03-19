/**
 * Messages Page
 * List of all conversations with chat functionality
 */

'use client'

import { useState } from 'react'
import { MessageCircle, Users } from 'lucide-react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import ChatList from '@/components/ChatList'

export default function MessagesPage() {
  const [view, setView] = useState<'list' | 'online'>('list')

  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Сообщения</h1>
        <p className="text-xl text-gray-600">
          Общайтесь с менторами и студентами в реальном времени
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={view === 'list' ? 'primary' : 'outline'}
          size="md"
          onClick={() => setView('list')}
        >
          <MessageCircle className="w-4 h-4 mr-2" />
          Диалоги
        </Button>
        <Button
          variant={view === 'online' ? 'primary' : 'outline'}
          size="md"
          onClick={() => setView('online')}
        >
          <Users className="w-4 h-4 mr-2" />
          Онлайн пользователи
        </Button>
      </div>

      {/* Content */}
      {view === 'list' ? (
        <ChatList />
      ) : (
        <Card padding="lg">
          <div className="text-center py-8">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Онлайн пользователи
            </h3>
            <p className="text-gray-600 mb-4">
              Список пользователей, которые сейчас онлайн
            </p>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">
                Функция в разработке...
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Tips */}
      <Card padding="lg" className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 border border-indigo-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4">💡 Как это работает</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-2xl mb-2">💬</div>
            <h4 className="font-semibold text-gray-900 mb-1">Real-time чат</h4>
            <p className="text-sm text-gray-600">
              Сообщения доставляются мгновенно через WebSocket соединение
            </p>
          </div>
          <div>
            <div className="text-2xl mb-2">📱</div>
            <h4 className="font-semibold text-gray-900 mb-1">Уведомления</h4>
            <p className="text-sm text-gray-600">
              Получайте уведомления о новых сообщениях в реальном времени
            </p>
          </div>
          <div>
            <div className="text-2xl mb-2">✅</div>
            <h4 className="font-semibold text-gray-900 mb-1">Статус прочтения</h4>
            <p className="text-sm text-gray-600">
              Отслеживайте, когда сообщения прочитаны
            </p>
          </div>
        </div>
      </Card>
    </main>
  )
}
