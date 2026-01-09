/**
 * Chat Button Component
 * Floating button to open chat with a mentor/student
 */

'use client'

import { useState } from 'react'
import { MessageCircle } from 'lucide-react'
import { ChatWidget } from './ChatWidget'

interface ChatButtonProps {
  recipientId: number
  recipientName: string
  initialMessage?: string
}

export function ChatButton({ recipientId, recipientName }: ChatButtonProps) {
  const [isChatOpen, setIsChatOpen] = useState(false)

  return (
    <>
      {/* Floating Chat Button */}
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all duration-300 flex items-center justify-center z-40 group"
        aria-label={`Chat with ${recipientName}`}
      >
        <MessageCircle className="w-6 h-6 group-hover:scale-110 transition-transform" />
        <span className="sr-only">Open chat with {recipientName}</span>
      </button>

      {/* Chat Widget */}
      <ChatWidget
        recipientId={recipientId}
        recipientName={recipientName}
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />

      {/* Online Status Indicator (optional) */}
      <div className="fixed bottom-24 right-6 flex items-center gap-2 bg-white px-3 py-1 rounded-full shadow-md border border-gray-200">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span className="text-xs text-gray-600">Online now</span>
      </div>
    </>
  )
}