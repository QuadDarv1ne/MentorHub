import { NextRequest, NextResponse } from 'next/server'
import { getSession } from 'next-auth/react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL
if (!BACKEND_URL) {
  throw new Error('NEXT_PUBLIC_BACKEND_URL environment variable is required for calls token API')
}

export async function POST(request: NextRequest) {
  try {
    // Проверяем авторизацию
    const session = await getSession()
    if (!session?.accessToken) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { channel_id, participant_id, room_id } = body

    // Запрос к бэкенду за токеном Agora
    const response = await fetch(`${BACKEND_URL}/api/calls/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.accessToken}`
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
    console.error('Calls API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
