import { NextRequest, NextResponse } from 'next/server'
import { logger } from '@/lib/utils/logger'
import { getBackendUrl, extractBearerToken } from '@/lib/api/server-url'

export async function GET(request: NextRequest) {
  try {
    const token = extractBearerToken(request)
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const endpoint = searchParams.get('endpoint') || 'platform'
    const days = searchParams.get('days') || '30'

    let apiUrl = `${getBackendUrl()}/api/analytics/${endpoint}`
    if (endpoint !== 'platform') {
      apiUrl += `?days=${days}`
    }

    const response = await fetch(apiUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    logger.error('Analytics API error:', error as Error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
