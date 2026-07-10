/**
 * Messages API - History endpoint
 * Proxy to backend messages API for message history
 */

import { NextRequest, NextResponse } from 'next/server'
import { getBackendUrl, extractBearerToken } from '@/lib/api/server-url'

export async function GET(
  request: NextRequest,
  { params }: { params: { userId: string } }
) {
  try {
    const token = extractBearerToken(request)
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const limit = searchParams.get('limit') || '50'
    const before = searchParams.get('before') || ''

    let url = `${getBackendUrl()}/api/messages/history/${params.userId}?limit=${limit}`
    
    if (before) {
      url += `&before=${encodeURIComponent(before)}`
    }

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
