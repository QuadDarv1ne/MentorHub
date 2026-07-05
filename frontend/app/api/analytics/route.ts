import { NextRequest, NextResponse } from 'next/server'
import { logger } from '@/lib/utils/logger'

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL
if (!BACKEND_URL) {
  throw new Error('BACKEND_URL environment variable is required for analytics API')
}

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    const token = authHeader.slice(7)

    const { searchParams } = new URL(request.url)
    const endpoint = searchParams.get('endpoint') || 'platform'
    const days = searchParams.get('days') || '30'

    let apiUrl = `${BACKEND_URL}/api/analytics/${endpoint}`
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
