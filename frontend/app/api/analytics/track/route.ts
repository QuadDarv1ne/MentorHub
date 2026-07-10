import { NextRequest, NextResponse } from 'next/server'
import { logger } from '@/lib/utils/logger'
import { getBackendUrl } from '@/lib/api/server-url'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { event_type, user_id, page_url, timestamp, metadata } = body

    // Валидация события
    if (!event_type || !page_url) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Отправка события в backend
    const response = await fetch(`${getBackendUrl()}/api/analytics/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        event_type,
        user_id,
        page_url,
        timestamp,
        metadata
      })
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    logger.error('Analytics track error:', error as Error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
