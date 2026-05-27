import { NextRequest, NextResponse } from 'next/server'
import { getSession } from 'next-auth/react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL
if (!BACKEND_URL) {
  throw new Error('NEXT_PUBLIC_BACKEND_URL environment variable is required for export API')
}

export async function POST(request: NextRequest) {
  try {
    const session = await getSession()
    if (!session?.accessToken) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const format = searchParams.get('format') || 'json'
    const type = searchParams.get('type') || 'users'

    const body = await request.json()
    const { date_from, date_to, user_ids, course_ids } = body

    // Запрос к бэкенду за экспортом
    const params = new URLSearchParams({ format })
    if (type) params.append('type', type)

    const response = await fetch(`${BACKEND_URL}/api/export/data?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${session.accessToken}`
      }
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    // Получаем файл с бэкенда
    const blob = await response.blob()
    const contentType = response.headers.get('content-type') || 'application/octet-stream'
    const contentDisposition = response.headers.get('content-disposition')
    
    let filename = `export.${format}`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename=(.+)/)
      if (match) {
        filename = match[1]
      }
    }

    return new NextResponse(blob, {
      headers: {
        'Content-Type': contentType || 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${filename}"`
      }
    })
  } catch (error) {
    console.error('Export API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
