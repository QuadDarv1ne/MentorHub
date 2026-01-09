/**
 * Real-time Chat Widget Component
 * WebSocket-powered chat between students and mentors
 */

'use client'

import { useState, useEffect, useRef } from 'react'
import { Send, X, MessageCircle, User, Check, CheckCheck } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

interface Message {
  id: number
  sender_id: number
  sender_username: string
  sender_avatar?: string
  recipient_id: number
  content: string
  timestamp: string
  is_read?: boolean
}

interface ChatWidgetProps {
  recipientId: number
  recipientName: string
  isOpen: boolean
  onClose: () => void
}

export function ChatWidget({ recipientId, recipientName, isOpen, onClose }: ChatWidgetProps) {
  const { getToken } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting')
  const [ws, setWs] = useState<WebSocket | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const typingTimeoutRef = useRef<NodeJS.Timeout>()

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // WebSocket connection
  useEffect(() => {
    const token = getToken()
    if (!isOpen || !token) return

    const websocketUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/chat?token=${token}`
    const socket = new WebSocket(websocketUrl)

    socket.onopen = () => {
      console.log('✅ WebSocket connected')
      setConnectionStatus('connected')
      setWs(socket)
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        switch (data.type) {
          case 'message':
            setMessages(prev => [...prev, data])
            break
          case 'typing':
            setIsTyping(true)
            setTimeout(() => setIsTyping(false), 3000)
            break
          case 'read':
            setMessages(prev => 
              prev.map(msg => 
                msg.id === data.message_id 
                  ? { ...msg, is_read: true } 
                  : msg
              )
            )
            break
          case 'connected':
            console.log('Connected as:', data.username)
            break
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('disconnected')
    }

    socket.onclose = () => {
      console.log('WebSocket disconnected')
      setConnectionStatus('disconnected')
    }

    return () => {
      socket.close()
    }
  }, [isOpen, getToken])

  const sendMessage = () => {
    if (!newMessage.trim() || !ws || ws.readyState !== WebSocket.OPEN) return

    const messageData = {
      type: 'message',
      recipient_id: recipientId,
      content: newMessage.trim()
    }

    ws.send(JSON.stringify(messageData))
    setNewMessage('')
  }

  const sendTypingIndicator = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    ws.send(JSON.stringify({
      type: 'typing',
      recipient_id: recipientId
    }))

    typingTimeoutRef.current = setTimeout(() => {
      // Typing stopped
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[500px] bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{recipientName}</h3>
            <div className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-500' : 
                connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className="text-xs text-gray-500 capitalize">
                {connectionStatus === 'connected' ? 'Online' : 
                 connectionStatus === 'connecting' ? 'Connecting...' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-gray-200 transition-colors"
          aria-label="Close chat"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">Start the conversation</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender_id === 1 ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] rounded-lg p-3 ${
                message.sender_id === 1 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <p className="text-sm">{message.content}</p>
                <div className="flex items-center justify-end gap-1 mt-1">
                  <span className="text-xs opacity-70">
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  {message.sender_id === 1 && (
                    message.is_read ? (
                      <CheckCheck className="w-3 h-3 opacity-70" />
                    ) : (
                      <Check className="w-3 h-3 opacity-70" />
                    )
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <textarea
              value={newMessage}
              onChange={(e) => {
                setNewMessage(e.target.value)
                sendTypingIndicator()
              }}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
              disabled={connectionStatus !== 'connected'}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!newMessage.trim() || connectionStatus !== 'connected'}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Send message"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}