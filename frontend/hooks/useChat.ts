/**
 * useChat Hook
 * WebSocket-powered chat hook for real-time messaging
 */

'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useToast } from '@/components/ui/ToastContext'
import { TIMEOUTS, RETRY, LIMITS, STORAGE_KEYS } from '@/lib/constants'
import { apiRequest, getBaseUrl } from '@/lib/api/client'
import { logger } from '@/lib/utils/logger'

export interface Message {
  id: number
  sender_id: number
  sender_username: string
  sender_avatar?: string
  recipient_id: number
  content: string
  timestamp: string
  is_read?: boolean
}

export interface Conversation {
  user_id: number
  username: string
  avatar_url?: string
  last_message: string
  last_message_time: string
  unread_count: number
  is_from_me: boolean
}

interface UseChatOptions {
  recipientId?: number
  autoReconnect?: boolean
  maxReconnectAttempts?: number
}

export function useChat({
  recipientId,
  autoReconnect = true,
  maxReconnectAttempts = RETRY.MAX_ATTEMPTS,
  enableNotifications = true
}: UseChatOptions & { enableNotifications?: boolean } = {}) {
  const toast = useToast()
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const typingTimeoutRef = useRef<NodeJS.Timeout>()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const enableNotificationsRef = useRef(enableNotifications)
  const toastRef = useRef(toast)
  enableNotificationsRef.current = enableNotifications
  toastRef.current = toast

  // Load message history
  const loadMessageHistory = useCallback(async (userId: number, limit = LIMITS.MAX_MESSAGE_LENGTH / 2) => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await apiRequest<{ messages: Message[] }>(`/messages/history/${userId}?limit=${limit}`)
      setMessages(data.messages || [])
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Load conversations list
  const loadConversations = useCallback(async () => {
    try {
      const data = await apiRequest<Conversation[]>('/messages/conversations')
      setConversations(data)
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      return null
    }
  }, [])

  // Connect to WebSocket
  const connect = useCallback(() => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    if (!token) {
      setConnectionStatus('disconnected')
      return
    }

    setConnectionStatus('connecting')

    const baseUrl = getBaseUrl().replace('http', 'ws')
    const wsUrl = `${baseUrl}/ws/chat`
    const socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      // Send auth message
      socket.send(JSON.stringify({
        type: 'auth',
        token: token
      }))
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        switch (data.type) {
          case 'connected':
            setConnectionStatus('connected')
            reconnectAttemptsRef.current = 0
            break

          case 'message':
            setMessages(prev => {
              // Avoid duplicates
              if (prev.some(m => m.id === data.id)) {
                return prev
              }
              return [...prev, data]
            })
            // Show toast notification for new messages from others
            if (enableNotificationsRef.current && data.sender_id !== parseInt(localStorage.getItem('user_id') || '0')) {
              toastRef.current.showToast(`Новое сообщение от ${data.sender_username}`, 'info', 3000)
            }
            // Also update conversations
            setConversations(prev => {
              const idx = prev.findIndex(c => c.user_id === data.sender_id || c.user_id === data.recipient_id)
              if (idx >= 0) {
                const updated = [...prev]
                updated[idx] = {
                  ...updated[idx],
                  last_message: data.content,
                  last_message_time: data.timestamp,
                  unread_count: data.recipient_id === parseInt(localStorage.getItem('user_id') || '0') ? 1 : 0,
                  is_from_me: data.sender_id === parseInt(localStorage.getItem('user_id') || '0')
                }
                return updated
              }
              return prev
            })
            break

          case 'typing':
            setIsTyping(true)
            if (typingTimeoutRef.current) {
              clearTimeout(typingTimeoutRef.current)
            }
            typingTimeoutRef.current = setTimeout(() => setIsTyping(false), TIMEOUTS.TYPING_INDICATOR)
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

          case 'error':
            setError(data.message)
            break
        }
      } catch (err) {
        logger.error('Error parsing WebSocket message', err)
      }
    }

    socket.onerror = () => {
      setConnectionStatus('disconnected')
      setError('WebSocket connection error')
    }

    socket.onclose = () => {
      setConnectionStatus('disconnected')

      // Auto-reconnect
      if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
        reconnectAttemptsRef.current += 1
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
        reconnectTimeoutRef.current = setTimeout(connect, delay)
      }
    }

    wsRef.current = socket
  }, [autoReconnect, maxReconnectAttempts])

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = undefined
    }

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
      typingTimeoutRef.current = undefined
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close()
    }

    wsRef.current = null
    setConnectionStatus('disconnected')
  }, [])

  // Send message
  const sendMessage = useCallback(() => {
    if (!newMessage.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return false
    }

    const messageData = {
      type: 'message',
      recipient_id: recipientId,
      content: newMessage.trim()
    }

    wsRef.current.send(JSON.stringify(messageData))
    setNewMessage('')
    return true
  }, [newMessage, recipientId])

  // Send typing indicator
  const sendTypingIndicator = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    wsRef.current.send(JSON.stringify({
      type: 'typing',
      recipient_id: recipientId
    }))

    typingTimeoutRef.current = setTimeout(() => {
      // Typing stopped
    }, 1000)
  }, [recipientId])

  // Mark message as read
  const markAsRead = useCallback((messageId: number) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

    wsRef.current.send(JSON.stringify({
      type: 'read',
      message_id: messageId
    }))
  }, [])

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // Initial connection
  useEffect(() => {
    if (recipientId) {
      connect()
      loadMessageHistory(recipientId)
    }

    return () => {
      disconnect()
    }
  }, [recipientId, connect, disconnect, loadMessageHistory])

  // Auto-scroll on new messages
  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
    }
  }, [])

  return {
    // State
    messages,
    conversations,
    newMessage,
    setNewMessage,
    isTyping,
    connectionStatus,
    isLoading,
    error,

    // Actions
    connect,
    disconnect,
    sendMessage,
    sendTypingIndicator,
    markAsRead,
    loadMessageHistory,
    loadConversations,
    scrollToBottom,

    // Refs
    messagesEndRef,
    wsRef
  }
}

export default useChat
