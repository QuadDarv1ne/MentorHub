/**
 * useWebSocket Hook
 * Shared WebSocket connection with automatic reconnection and exponential backoff
 */

'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { getBaseUrl } from '@/lib/api/client'
import { STORAGE_KEYS, RETRY } from '@/lib/constants'
import { logger } from '@/lib/utils/logger'

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected'

export interface UseWebSocketOptions {
  /** WebSocket endpoint path (e.g., '/ws/chat') */
  path: string
  /** Enable automatic reconnection (default: true) */
  autoReconnect?: boolean
  /** Maximum reconnection attempts (default: RETRY.MAX_ATTEMPTS) */
  maxReconnectAttempts?: number
  /** Token query parameter name (default: 'token') */
  tokenParam?: string
  /** Whether to include token in URL query param (default: false, uses auth message instead) */
  useQueryParam?: boolean
  /** Callback when connection status changes */
  onStatusChange?: (status: ConnectionStatus) => void
  /** Callback when message is received */
  onMessage?: (data: Record<string, unknown>) => void
}

export interface UseWebSocketReturn {
  /** Current connection status */
  connectionStatus: ConnectionStatus
  /** Send a JSON message through the WebSocket */
  sendMessage: (data: Record<string, unknown>) => void
  /** Manually connect to the WebSocket */
  connect: () => void
  /** Manually disconnect from the WebSocket */
  disconnect: () => void
  /** The raw WebSocket instance */
  socketRef: React.MutableRefObject<WebSocket | null>
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    path,
    autoReconnect = true,
    maxReconnectAttempts = RETRY.MAX_ATTEMPTS,
    tokenParam = 'token',
    useQueryParam = false,
    onStatusChange,
    onMessage,
  } = options

  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected')
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const updateStatus = useCallback((status: ConnectionStatus) => {
    setConnectionStatus(status)
    onStatusChange?.(status)
  }, [onStatusChange])

  const connect = useCallback(() => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    if (!token) {
      updateStatus('disconnected')
      return
    }

    updateStatus('connecting')

    const baseUrl = getBaseUrl().replace('http', 'ws')
    const url = useQueryParam
      ? `${baseUrl}${path}?${tokenParam}=${token}`
      : `${baseUrl}${path}`

    const socket = new WebSocket(url)

    socket.onopen = () => {
      if (!useQueryParam) {
        socket.send(JSON.stringify({ type: 'auth', token }))
      }
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'connected') {
          updateStatus('connected')
          reconnectAttemptsRef.current = 0
        }
        onMessage?.(data)
      } catch (err) {
        logger.error('WebSocket message parse error', err)
      }
    }

    socket.onerror = () => {
      updateStatus('disconnected')
    }

    socket.onclose = () => {
      updateStatus('disconnected')
      if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
        reconnectAttemptsRef.current += 1
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
        reconnectTimeoutRef.current = setTimeout(connect, delay)
      }
    }

    socketRef.current = socket
  }, [path, autoReconnect, maxReconnectAttempts, useQueryParam, tokenParam, updateStatus, onMessage])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = undefined
    }
    reconnectAttemptsRef.current = maxReconnectAttempts
    if (socketRef.current) {
      socketRef.current.close()
      socketRef.current = null
    }
  }, [maxReconnectAttempts])

  const sendMessage = useCallback((data: Record<string, unknown>) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(data))
    }
  }, [])

  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socketRef.current) {
        socketRef.current.close()
      }
    }
  }, [])

  return {
    connectionStatus,
    sendMessage,
    connect,
    disconnect,
    socketRef,
  }
}
