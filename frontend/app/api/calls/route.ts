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
    const { participant_id, room_id } = body

    const response = await fetch(`${getBackendUrl()}/api/calls/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        participant_id,
        room_id
      })
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    const callData = await response.json()
    return NextResponse.json(callData)
  } catch (error) {
    logger.error('Create call API error:', error as Error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
