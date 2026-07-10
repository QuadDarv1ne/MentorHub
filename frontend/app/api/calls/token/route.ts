import { NextRequest, NextResponse } from 'next/server'
import { logger } from '@/lib/utils/logger'
import { getBackendUrl, extractBearerToken } from '@/lib/api/server-url'

export async function POST(request: NextRequest) {
  try {
    const token = extractBearerToken(request)
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { channel_id, participant_id, room_id } = body

    const response = await fetch(`${getBackendUrl()}/api/calls/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        channel_id,
        participant_id,
        room_id
      })
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    const tokenData = await response.json()
    return NextResponse.json(tokenData)
  } catch (error) {
    logger.error('Calls API error:', error as Error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
