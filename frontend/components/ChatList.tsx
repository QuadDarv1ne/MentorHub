/**
 * Chat List Component
 * Displays list of conversations with unread counts
 */

'use client'

import { useState, useEffect } from 'react'
import { MessageCircle, ChevronRight } from 'lucide-react'
import useChat, { Conversation } from '@/hooks/useChat'
import { ChatWidget } from './ChatWidget'

interface ChatListProps {
  onConversationSelect?: (conversation: Conversation) => void
}

export function ChatList({ onConversationSelect }: ChatListProps) {
  const { conversations, loadConversations, isLoading, error } = useChat()
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [isChatOpen, setIsChatOpen] = useState(false)

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  const handleConversationClick = (conversation: Conversation) => {
    setSelectedConversation(conversation)
    setIsChatOpen(true)
    onConversationSelect?.(conversation)
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (days === 1) {
      return 'Вчера'
    } else if (days < 7) {
      return date.toLocaleDateString([], { weekday: 'short' })
    } else {
      return date.toLocaleDateString([], { day: 'numeric', month: 'short' })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500 text-sm">{error}</p>
      </div>
    )
  }

  if (conversations.length === 0) {
    return (
      <div className="text-center p-8">
        <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Нет сообщений</h3>
        <p className="text-gray-500 text-sm">
          Начните общение с ментором или студентом
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="divide-y divide-gray-200">
          {conversations.map((conversation) => (
            <button
              key={conversation.user_id}
              onClick={() => handleConversationClick(conversation)}
              className="w-full p-4 hover:bg-gray-50 transition-colors flex items-center gap-3"
            >
              {/* Avatar */}
              <div className="relative flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                  {conversation.avatar_url ? (
                    <img
                      src={conversation.avatar_url}
                      alt={conversation.username}
                      className="w-full h-full rounded-full object-cover"
                    />
                  ) : (
                    conversation.username?.charAt(0)?.toUpperCase() || '?'
                  )}
                </div>
                {/* Online indicator */}
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 text-left">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-semibold text-gray-900 truncate">
                    {conversation.username}
                  </h4>
                  <span className="text-xs text-gray-500 flex-shrink-0">
                    {formatTime(conversation.last_message_time)}
                  </span>
                </div>
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm text-gray-600 truncate">
                    {conversation.is_from_me && 'Вы: '}
                    {conversation.last_message}
                  </p>
                  {conversation.unread_count > 0 && (
                    <span className="flex-shrink-0 inline-flex items-center justify-center w-5 h-5 bg-indigo-600 text-white text-xs font-semibold rounded-full">
                      {conversation.unread_count}
                    </span>
                  )}
                </div>
              </div>

              {/* Arrow */}
              <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {/* Chat Widget */}
      {selectedConversation && (
        <ChatWidget
          recipientId={selectedConversation.user_id}
          recipientName={selectedConversation.username}
          isOpen={isChatOpen}
          onClose={() => {
            setIsChatOpen(false)
            setSelectedConversation(null)
          }}
        />
      )}
    </>
  )
}

export default ChatList
