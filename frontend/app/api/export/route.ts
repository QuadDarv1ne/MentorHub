import { NextRequest, NextResponse } from 'next/server'
import { logger } from '@/lib/utils/logger'
import { getBackendUrl, extractBearerToken } from '@/lib/api/server-url'

export async function POST(request: NextRequest) {
  try {
    const token = extractBearerToken(request)
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const format = searchParams.get('format') || 'json'
    const type = searchParams.get('type') || 'users'

    const body = await request.json()
    const { date_from: _date_from, date_to: _date_to, user_ids: _user_ids, course_ids: _course_ids } = body

    // Запрос к бэкенду за экспортом
    const params = new URLSearchParams({ format })
    if (type) params.append('type', type)

    const response = await fetch(`${getBackendUrl()}/api/export/data?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
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
    logger.error('Export API error:', error as Error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
