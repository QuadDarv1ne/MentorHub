'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Search, Send, MoreVertical, Paperclip, Phone, Video } from 'lucide-react'
import Badge from '@/components/ui/Badge'
import { useAuth } from '@/hooks/useAuth'

interface Message {
  id: string
  content: string
  timestamp: string
  sender: 'user' | 'other'
  type: 'text' | 'file' | 'image'
}

interface Conversation {
  id: string
  participantName: string
  participantAvatar: string
  lastMessage: string
  timestamp: string
  unread: number
  isOnline: boolean
  messages: Message[]
}

export default function MessagesPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedConversation, setSelectedConversation] = useState<string | null>('1')
  const [messageInput, setMessageInput] = useState('')
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: '1',
      participantName: 'Иван Петров',
      participantAvatar: '👨‍💻',
      lastMessage: 'Давайте встретимся в пятницу',
      timestamp: '10:30',
      unread: 2,
      isOnline: true,
      messages: [
        { id: '1', content: 'Привет! Как дела?', timestamp: '09:15', sender: 'other', type: 'text' },
        { id: '2', content: 'Все хорошо, спасибо за вопрос! 😊', timestamp: '09:20', sender: 'user', type: 'text' },
        { id: '3', content: 'Давайте встретимся в пятницу', timestamp: '10:30', sender: 'other', type: 'text' },
      ]
    },
    {
      id: '2',
      participantName: 'Мария Сидорова',
      participantAvatar: '👩‍💼',
      lastMessage: 'Спасибо за отзывы!',
      timestamp: '09:45',
      unread: 0,
      isOnline: true,
      messages: [
        { id: '1', content: 'Спасибо за отзывы!', timestamp: '09:45', sender: 'other', type: 'text' },
      ]
    },
    {
      id: '3',
      participantName: 'Алексей Иванов',
      participantAvatar: '👨‍🏫',
      lastMessage: 'Проверил задание',
      timestamp: 'вчера',
      unread: 0,
      isOnline: false,
      messages: [
        { id: '1', content: 'Проверил задание', timestamp: 'вчера', sender: 'other', type: 'text' },
      ]
    },
    {
      id: '4',
      participantName: 'Екатерина Петрова',
      participantAvatar: '👩‍💻',
      lastMessage: 'Поговорим позже',
      timestamp: 'пн',
      unread: 1,
      isOnline: false,
      messages: [
        { id: '1', content: 'Поговорим позже', timestamp: 'пн', sender: 'other', type: 'text' },
      ]
    },
  ])

  const filteredConversations = conversations.filter(conv =>
    conv.participantName.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const currentConversation = conversations.find(c => c.id === selectedConversation)

  const handleSendMessage = () => {
    if (!messageInput.trim() || !selectedConversation) return

    setConversations(conversations.map(conv => {
      if (conv.id === selectedConversation) {
        return {
          ...conv,
          messages: [
            ...conv.messages,
            {
              id: Date.now().toString(),
              content: messageInput,
              timestamp: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
              sender: 'user',
              type: 'text'
            }
          ],
          lastMessage: messageInput,
          timestamp: 'только что'
        }
      }
      return conv
    }))
    setMessageInput('')
  }

  const totalUnread = conversations.reduce((sum, conv) => sum + conv.unread, 0)

  // Проверка авторизации
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login?redirect=/messages')
    } else {
      setIsLoading(true)
      setTimeout(() => setIsLoading(false), 300)
    }
  }, [isAuthenticated, router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600">Загрузка сообщений...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto h-screen flex flex-col lg:flex-row">
        {/* Левая панель - Список диалогов */}
        <div className="w-full lg:w-80 border-r border-gray-200 bg-white flex flex-col">
          {/* Заголовок */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-2xl font-bold text-gray-900">Сообщения</h1>
              {totalUnread > 0 && (
                <Badge variant="danger">{totalUnread}</Badge>
              )}
            </div>

            {/* Поиск */}
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по диалогам..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Список диалогов */}
          <div className="flex-1 overflow-y-auto">
            {filteredConversations.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                Диалогов не найдено
              </div>
            ) : (
              filteredConversations.map(conv => (
                <button
                  key={conv.id}
                  onClick={() => setSelectedConversation(conv.id)}
                  className={`w-full px-4 py-3 border-b border-gray-100 hover:bg-gray-50 transition-colors text-left ${
                    selectedConversation === conv.id ? 'bg-indigo-50 border-l-4 border-l-indigo-600' : ''
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="relative flex-shrink-0">
                      <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-xl">
                        {conv.participantAvatar}
                      </div>
                      {conv.isOnline && (
                        <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="font-semibold text-gray-900 truncate">{conv.participantName}</p>
                        <span className="text-xs text-gray-500 ml-2">{conv.timestamp}</span>
                      </div>
                      <p className={`text-sm truncate ${conv.unread > 0 ? 'font-semibold text-gray-900' : 'text-gray-600'}`}>
                        {conv.lastMessage}
                      </p>
                    </div>
                    {conv.unread > 0 && (
                      <Badge variant="info" className="ml-2">{conv.unread}</Badge>
                    )}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Правая панель - Чат */}
        <div className="hidden lg:flex flex-1 flex-col bg-white">
          {currentConversation ? (
            <>
              {/* Заголовок чата */}
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-xl">
                      {currentConversation.participantAvatar}
                    </div>
                    {currentConversation.isOnline && (
                      <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                    )}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{currentConversation.participantName}</p>
                    <p className="text-sm text-gray-500">
                      {currentConversation.isOnline ? 'онлайн' : 'был(а) в сети'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Звонок">
                    <Phone size={20} className="text-gray-600" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Видеозвонок">
                    <Video size={20} className="text-gray-600" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Ещё">
                    <MoreVertical size={20} className="text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Сообщения */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {currentConversation.messages.map(msg => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        msg.sender === 'user'
                          ? 'bg-indigo-600 text-white rounded-br-none'
                          : 'bg-gray-100 text-gray-900 rounded-bl-none'
                      }`}
                    >
                      <p className="break-words">{msg.content}</p>
                      <p className={`text-xs mt-1 ${msg.sender === 'user' ? 'text-indigo-100' : 'text-gray-500'}`}>
                        {msg.timestamp}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Ввод сообщения */}
              <div className="px-6 py-4 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Прикрепить файл">
                    <Paperclip size={20} className="text-gray-600" />
                  </button>
                  <input
                    type="text"
                    placeholder="Напишите сообщение..."
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!messageInput.trim()}
                    className="p-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white rounded-lg transition-colors"
                    title="Отправить"
                  >
                    <Send size={20} />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <p>Выберите диалог для начала общения</p>
            </div>
          )}
        </div>

        {/* Мобильное предупреждение */}
        <div className="lg:hidden flex-1 flex items-center justify-center text-center text-gray-500 p-4">
          <p>Откройте диалог в полноэкранном режиме 📱</p>
        </div>
      </div>
    </div>
  )
}
