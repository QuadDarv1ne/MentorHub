'use client'

import { useState } from 'react'
import VideoCall from '@/components/VideoCall'
import { useToast } from '@/hooks/useToast'
import { apiRequest } from '@/lib/api/client'

export default function VideoCallPage() {
  const toast = useToast()
  const [activeCall, setActiveCall] = useState<{
    type: 'one-on-one' | 'group'
    participantId?: number
    roomId?: number
  } | null>(null)

  const startOneOnOneCall = async (participantId: number) => {
    try {
      const call = await apiRequest<any>('/calls/', {
        method: 'POST',
        body: JSON.stringify({ participant_id: participantId })
      })
      setActiveCall({
        type: 'one-on-one',
        participantId: call.participant_id
      })
    } catch {
      toast.error('Не удалось начать звонок')
    }
  }

  const startGroupCall = async (roomId: number) => {
    try {
      const call = await apiRequest<any>('/calls/', {
        method: 'POST',
        body: JSON.stringify({ room_id: roomId })
      })
      setActiveCall({
        type: 'group',
        roomId: call.room_id
      })
    } catch {
      toast.error('Не удалось начать групповой звонок')
    }
  }

  if (activeCall) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
        <VideoCall
          participantId={activeCall.participantId}
          roomId={activeCall.roomId}
          isGroupCall={activeCall.type === 'group'}
          onClose={() => setActiveCall(null)}
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Видеозвонки
        </h1>

        <div className="grid md:grid-cols-2 gap-6">
          {/* One-on-One Call Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Индивидуальный звонок
                </h2>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Позвонить ментору или ученику
                </p>
              </div>
            </div>

            <button
              onClick={() => startOneOnOneCall(1)} // Demo ID
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 px-4 rounded-lg transition-colors font-medium"
            >
              📞 Начать звонок
            </button>
          </div>

          {/* Group Call Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Групповой звонок
                </h2>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Созвать встречу с командой
                </p>
              </div>
            </div>

            <button
              onClick={() => startGroupCall(1)} // Demo ID
              className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg transition-colors font-medium"
            >
              👥 Начать групповой звонок
            </button>
          </div>
        </div>

        {/* Recent Calls */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
           Recent Calls
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {[1, 2, 3].map((call) => (
                <div key={call} className="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
                      <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        Звонок #{call}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        2 часа назад
                      </p>
                    </div>
                  </div>
                  <button className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium">
                    Перезвонить
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
