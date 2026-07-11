'use client'

import { useState, useEffect, useRef } from 'react'
import Image from 'next/image'
import { useToast } from '@/hooks/useToast'
import { logger } from '@/lib/utils/logger'

interface Message {
  id: number
  sender_id: number
  sender_name: string
  sender_avatar?: string
  content: string
  file_url?: string
  file_type?: 'image' | 'document' | 'audio'
  reactions: Record<string, string[]>
  created_at: string
  is_read: boolean
}

interface ChatRoom {
  id: number
  name?: string
  type: 'direct' | 'group'
  participants: { id: number; name: string; avatar?: string }[]
  last_message?: Message
  unread_count: number
}

export default function EnhancedChat() {
  const toast = useToast()
  const [rooms, setRooms] = useState<ChatRoom[]>([])
  const [selectedRoom, setSelectedRoom] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [showNewGroupModal, setShowNewGroupModal] = useState(false)
  const [groupName, setGroupName] = useState('')
  const [selectedParticipants, setSelectedParticipants] = useState<number[]>([])
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [uploadingFile, setUploadingFile] = useState<File | null>(null)
  const [typingUsers, setTypingUsers] = useState<string[]>([])
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const typingTimeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map())

  useEffect(() => {
    fetchRooms()
    connectWebSocket()
    const typingTimeouts = typingTimeoutsRef.current
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      typingTimeouts.forEach(timeout => clearTimeout(timeout))
      typingTimeouts.clear()
      wsRef.current?.close()
    }
  // Deps intentionally empty: runs once on mount
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (selectedRoom) {
      fetchMessages(selectedRoom)
      markAsRead(selectedRoom)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedRoom])

  const fetchRooms = async () => {
    try {
      const response = await fetch('/api/chat/rooms')
      if (response.ok) {
        const data = await response.json()
        setRooms(data)
        if (Array.isArray(data) && data.length > 0 && selectedRoom === null) {
          setSelectedRoom(data[0].id)
        }
      }
    } catch (error) {
      logger.error('Fetch rooms error:', error)
    }
  }

  const fetchMessages = async (roomId: number) => {
    try {
      const response = await fetch(`/api/chat/rooms/${roomId}/messages`)
      if (response.ok) {
        const data = await response.json()
        setMessages(data)
        setTimeout(scrollToBottom, 100)
      }
    } catch (error) {
      logger.error('Fetch messages error:', error)
    }
  }

  const connectWebSocket = () => {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/chat`
    
    try {
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        logger.info('Chat WebSocket connected')
      }

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'new_message') {
            if (data.room_id === selectedRoom) {
              setMessages(prev => [...prev, data.message])
              scrollToBottom()
            }
            // Update room's last message
            setRooms(prev => prev.map(room => 
              room.id === data.room_id 
                ? { ...room, last_message: data.message }
                : room
            ))
          }
          
          if (data.type === 'typing') {
            if (data.room_id === selectedRoom) {
              setTypingUsers(prev => [...new Set([...prev, data.user_name])])
              // Очищаем предыдущий timeout
              if (typingTimeoutsRef.current.has(data.user_name)) {
                clearTimeout(typingTimeoutsRef.current.get(data.user_name))
              }
              const timeout = setTimeout(() => {
                setTypingUsers(prev => prev.filter(u => u !== data.user_name))
                typingTimeoutsRef.current.delete(data.user_name)
              }, 3000)
              typingTimeoutsRef.current.set(data.user_name, timeout)
            }
          }
          
          if (data.type === 'reaction') {
            setMessages(prev => prev.map(msg => 
              msg.id === data.message_id 
                ? { ...msg, reactions: data.reactions }
                : msg
            ))
          }
        } catch (error) {
          logger.error('Parse message error:', error)
        }
      }

      wsRef.current.onclose = () => {
        logger.warn('Chat WebSocket disconnected')
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000)
      }
    } catch (error) {
      logger.error('WebSocket connection error:', error)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim() && !uploadingFile) return
    if (!selectedRoom) return

    try {
      const formData = new FormData()
      formData.append('content', newMessage)
      formData.append('room_id', selectedRoom.toString())
      
      if (uploadingFile) {
        formData.append('file', uploadingFile)
      }

      const response = await fetch('/api/chat/messages', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        setNewMessage('')
        setUploadingFile(null)
        setShowFileUpload(false)
        // Message will be added via WebSocket
      } else {
        toast.error('Ошибка отправки сообщения')
      }
    } catch (error) {
      logger.error('Send message error:', error)
      toast.error('Ошибка отправки сообщения')
    }
  }

  const addReaction = async (messageId: number, emoji: string) => {
    try {
      await fetch(`/api/chat/messages/${messageId}/reactions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emoji })
      })
    } catch (error) {
      logger.error('Add reaction error:', error)
    }
  }

  const createGroupChat = async () => {
    try {
      const response = await fetch('/api/chat/rooms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: groupName,
          participant_ids: selectedParticipants,
          is_group: true
        })
      })

      if (response.ok) {
        toast.success('Группа создана')
        setShowNewGroupModal(false)
        setGroupName('')
        setSelectedParticipants([])
        fetchRooms()
      } else {
        toast.error('Ошибка создания группы')
      }
    } catch (error) {
      logger.error('Create group error:', error)
      toast.error('Ошибка создания группы')
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.size <= 10 * 1024 * 1024) { // 10MB limit
      setUploadingFile(file)
      setShowFileUpload(true)
    } else {
      toast.error('Файл слишком большой (макс. 10MB)')
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const markAsRead = async (roomId: number) => {
    try {
      await fetch(`/api/chat/rooms/${roomId}/read`, { method: 'POST' })
    } catch (error) {
      logger.error('Mark as read error:', error)
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex bg-gray-100 dark:bg-gray-900">
      {/* Sidebar - Rooms List */}
      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">💬 Чаты</h2>
            <button
              onClick={() => setShowNewGroupModal(true)}
              className="p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors"
              title="Создать группу"
            >
              ➕
            </button>
          </div>
        </div>

        {/* Rooms */}
        <div className="flex-1 overflow-y-auto">
          {rooms.map(room => (
            <div
              key={room.id}
              onClick={() => setSelectedRoom(room.id)}
              className={`p-4 border-b border-gray-100 dark:border-gray-700 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                selectedRoom === room.id ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''
              }`}
            >
              <div className="flex items-center gap-3">
                {room.type === 'group' ? (
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-lg">
                    👥
                  </div>
                ) : (
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-400 to-blue-400 flex items-center justify-center text-lg">
                    {room.participants?.[0]?.avatar || '👤'}
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                      {room.type === 'group' ? room.name : room.participants?.[0]?.name}
                    </h3>
                    {room.unread_count > 0 && (
                      <span className="ml-2 px-2 py-0.5 bg-red-500 text-white text-xs font-bold rounded-full">
                        {room.unread_count}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                    {room.last_message?.content || 'Нет сообщений'}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedRoom ? (
          <>
            {/* Chat Header */}
            <div className="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                  {rooms.find(r => r.id === selectedRoom)?.type === 'group'
                    ? rooms.find(r => r.id === selectedRoom)?.name
                    : rooms.find(r => r.id === selectedRoom)?.participants[0]?.name}
                </h3>
                {typingUsers.length > 0 && (
                  <p className="text-sm text-indigo-600 dark:text-indigo-400">
                    {typingUsers.join(', ')} печатают...
                  </p>
                )}
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
              {messages.map((message, _index) => {
                const currentUserId = typeof window !== 'undefined'
                  ? (() => {
                      try {
                        const user = localStorage.getItem('user')
                        return user ? JSON.parse(user)?.id : null
                      } catch {
                        return null
                      }
                    })()
                  : null
                const isOwn = message.sender_id === currentUserId
                return (
                  <div
                    key={message.id}
                    className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[70%] ${isOwn ? 'order-1' : 'order-2'}`}>
                      <div
                        className={`px-4 py-2 rounded-2xl ${
                          isOwn
                            ? 'bg-indigo-600 text-white'
                            : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
                        }`}
                      >
                        {!isOwn && (
                          <p className="text-xs font-semibold mb-1 opacity-75">
                            {message.sender_name}
                          </p>
                        )}
                        <p>{message.content}</p>
                        
                        {/* File Attachment */}
                        {message.file_url && (
                          <div className="mt-2">
                            {message.file_type === 'image' ? (
                              <div className="relative w-full h-48">
                                <Image src={message.file_url} alt="Attachment" fill className="rounded-lg object-contain" />
                              </div>
                            ) : (
                              <a
                                href={message.file_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 text-sm underline"
                              >
                                📎 {message.file_type === 'audio' ? 'Голосовое сообщение' : 'Файл'}
                              </a>
                            )}
                          </div>
                        )}
                      </div>
                      
                      {/* Message Info */}
                      <div className={`flex items-center gap-2 mt-1 text-xs text-gray-500 ${isOwn ? 'justify-end' : ''}`}>
                        <span>{formatTime(message.created_at)}</span>
                        {message.is_read && isOwn && <span>✓✓</span>}
                      </div>
                      
                      {/* Reactions */}
                      <div className="flex gap-1 mt-1">
                        {Object.entries(message.reactions).map(([emoji, users]) => (
                          <button
                            key={emoji}
                            onClick={() => addReaction(message.id, emoji)}
                            className="px-2 py-0.5 bg-white dark:bg-gray-800 rounded-full text-xs hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            {emoji} {users.length}
                          </button>
                        ))}
                        <button
                          onClick={() => {/* Show reaction picker */}}
                          className="px-2 py-0.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full text-xs"
                        >
                          😀
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
              
              {/* Typing indicator */}
              {typingUsers.length > 0 && (
                <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                  <span className="text-sm">Печатает...</span>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
              {/* File Upload Preview */}
              {showFileUpload && uploadingFile && (
                <div className="mb-2 p-2 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    📎 {uploadingFile.name}
                  </span>
                  <button
                    onClick={() => {
                      setShowFileUpload(false)
                      setUploadingFile(null)
                    }}
                    className="text-gray-500 hover:text-red-500"
                  >
                    ✕
                  </button>
                </div>
              )}
              
              <div className="flex items-center gap-2">
                {/* File Upload Button */}
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  accept="image/*,audio/*,application/pdf,.doc,.docx,.txt"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-gray-500 hover:text-indigo-600 transition-colors"
                  title="Прикрепить файл"
                >
                  📎
                </button>
                
                {/* Voice Message Button */}
                <button
                  className="p-2 text-gray-500 hover:text-indigo-600 transition-colors"
                  title="Голосовое сообщение"
                >
                  🎤
                </button>
                
                {/* Text Input */}
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Введите сообщение..."
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-full bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                
                {/* Send Button */}
                <button
                  onClick={sendMessage}
                  disabled={!newMessage.trim() && !uploadingFile}
                  className="p-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white rounded-full transition-colors"
                >
                  📤
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <span className="text-6xl mb-4 block">💬</span>
              <p className="text-xl">Выберите чат для начала общения</p>
            </div>
          </div>
        )}
      </div>

      {/* New Group Modal */}
      {showNewGroupModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Создать группу
            </h3>
            <input
              type="text"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              placeholder="Название группы"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-4"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowNewGroupModal(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Отмена
              </button>
              <button
                onClick={createGroupChat}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg"
              >
                Создать
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
