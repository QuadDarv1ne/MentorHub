'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useToast } from '@/hooks/useToast'
import { apiRequest } from '@/lib/api/client'
import { logger } from '@/lib/utils/logger'

interface VideoCallProps {
  channelId?: string
  participantId?: number
  roomId?: number
  isGroupCall?: boolean
  onClose?: () => void
}

interface AgoraClient {
  join: (token: string, channel: string, uid: number) => Promise<void>
  leave: () => Promise<void>
  publish: (track: any) => Promise<void>
  unpublish: (track: any) => Promise<void>
  subscribe: (user: any, mediaType: string) => Promise<void>
  on: (event: string, callback: (...args: any[]) => void) => void
  off: (event: string) => void
}

export default function VideoCall({
  channelId,
  participantId,
  roomId,
  isGroupCall = false,
  onClose
}: VideoCallProps) {
  const router = useRouter()
  const toast = useToast()
  const [, setIsConnected] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isVideoOff, setIsVideoOff] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const localVideoRef = useRef<HTMLVideoElement>(null)
  const remoteVideoRef = useRef<HTMLVideoElement>(null)
  const agoraClientRef = useRef<AgoraClient | null>(null)
  const localTrackRef = useRef<any>(null)

  useEffect(() => {
    initCall()
    return () => { cleanup() }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const initCall = async () => {
    try {
      // Получаем токен Agora с бэкенда
      const { token, channel, uid } = await apiRequest<{ token: string; channel: string; uid: number }>('/calls/token', {
        method: 'POST',
        body: JSON.stringify({
          channel_id: channelId,
          participant_id: participantId,
          room_id: roomId
        })
      })

      // Импортируем Agora SDK динамически
      const AgoraRTC = (await import('agora-rtc-react')).default
      
      // Создаем клиент
      const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })
      agoraClientRef.current = client as unknown as AgoraClient

      // Настраиваем обработчики событий
      client.on('user-published', async (user: any, mediaType: any) => {
        await client.subscribe(user, mediaType)
        if (mediaType === 'video') {
          user.videoTrack.play(remoteVideoRef.current)
        }
        if (mediaType === 'audio') {
          user.audioTrack.play()
        }
      })

      client.on('user-unpublished', async (user: any, mediaType: any) => {
        await client.unsubscribe(user, mediaType)
      })

      client.on('user-left', (user: any) => {
        logger.info('User left call:', user)
      })

      // Подключаемся к каналу
      await client.join(token, channel, String(uid))
      setIsConnected(true)

      // Создаем и публикуем локальные треки
      const localAudioTrack = await AgoraRTC.createMicrophoneAudioTrack()
      const localVideoTrack = await AgoraRTC.createCameraVideoTrack({
        encoderConfig: {
          width: 640,
          height: 480,
          frameRate: 15,
          bitrateMin: 200,
          bitrateMax: 1000
        }
      })

      localTrackRef.current = { audio: localAudioTrack, video: localVideoTrack }

      // Воспроизводим локальное видео
      if (localVideoRef.current) {
        localVideoTrack.play(localVideoRef.current)
      }

      // Публикуем треки
      await client.publish([localAudioTrack, localVideoTrack])

      setIsLoading(false)
      toast.success('Видеозвонок подключён')

    } catch (err: any) {
      logger.error('Video call init error:', err)
      setError(err.message || 'Failed to initialize video call')
      setIsLoading(false)
      toast.error('Ошибка подключения к видеозвонку')
    }
  }

  const toggleMute = () => {
    if (localTrackRef.current?.audio) {
      localTrackRef.current.audio.setEnabled(!isMuted)
      setIsMuted(!isMuted)
      toast.info(isMuted ? 'Микрофон включён' : 'Микрофон выключен')
    }
  }

  const toggleVideo = () => {
    if (localTrackRef.current?.video) {
      localTrackRef.current.video.setEnabled(!isVideoOff)
      setIsVideoOff(!isVideoOff)
      toast.info(isVideoOff ? 'Камера включена' : 'Камера выключена')
    }
  }

  const leaveCall = async () => {
    try {
      if (localTrackRef.current) {
        localTrackRef.current.audio.close()
        localTrackRef.current.video.close()
      }

      if (agoraClientRef.current) {
        await agoraClientRef.current.leave()
      }

      setIsConnected(false)
      toast.success('Звонок завершён')
      onClose?.()
      router.push('/calls')
    } catch (err) {
      logger.error('Leave call error:', err)
    }
  }

  const cleanup = async () => {
    try {
      if (localTrackRef.current) {
        localTrackRef.current.audio?.close()
        localTrackRef.current.video?.close()
      }
      if (agoraClientRef.current) {
        const client = agoraClientRef.current as any
        // Снимаем все event listeners перед уходом
        client.off('user-published')
        client.off('user-unpublished')
        client.off('user-left')
        await client.leave()
      }
    } catch (err) {
      logger.error('Cleanup error:', err)
    }
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px] bg-gray-900 rounded-lg">
        <div className="text-center text-white">
          <p className="text-xl mb-4">⚠️ {error}</p>
          <button
            onClick={leaveCall}
            className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg transition-colors"
          >
            Закрыть
          </button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] bg-gray-900 rounded-lg">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-lg">Подключение к видеозвонку...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full h-full bg-gray-900 rounded-lg overflow-hidden">
      {/* Remote video */}
      <div className="absolute inset-0">
        <video
          ref={remoteVideoRef}
          className="w-full h-full object-cover"
          autoPlay
          playsInline
        />
      </div>

      {/* Local video (PiP) */}
      <div className="absolute top-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden shadow-lg border-2 border-gray-700">
        <video
          ref={localVideoRef}
          className="w-full h-full object-cover"
          autoPlay
          playsInline
          muted
        />
        <div className="absolute bottom-2 left-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
          Вы
        </div>
      </div>

      {/* Controls */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6">
        <div className="flex items-center justify-center gap-4">
          {/* Mute button */}
          <button
            onClick={toggleMute}
            className={`p-4 rounded-full transition-colors ${
              isMuted
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
            title={isMuted ? 'Включить микрофон' : 'Выключить микрофон'}
          >
            {isMuted ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            )}
          </button>

          {/* End call button */}
          <button
            onClick={leaveCall}
            className="p-4 bg-red-600 hover:bg-red-700 rounded-full transition-colors"
            title="Завершить звонок"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.476-1.494a1 1 0 00-1.256.647l-.816 2.12a14.718 14.718 0 01-6.068-6.068l2.12-.816a1 1 0 00.647-1.256l-1.494-4.476A1 1 0 009.28 5H6a2 2 0 00-2 2z" />
            </svg>
          </button>

          {/* Video toggle button */}
          <button
            onClick={toggleVideo}
            className={`p-4 rounded-full transition-colors ${
              isVideoOff
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
            title={isVideoOff ? 'Включить камеру' : 'Выключить камеру'}
          >
            {isVideoOff ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3l18 18" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>
        </div>

        {/* Call info */}
        <div className="text-center text-white mt-4">
          <p className="text-sm">
            {isGroupCall ? 'Групповой звонок' : 'Звонок'} • 
            <span className="ml-2 text-green-400">● В сети</span>
          </p>
        </div>
      </div>
    </div>
  )
}
