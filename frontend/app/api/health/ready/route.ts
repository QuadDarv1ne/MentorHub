import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ status: 'ready', timestamp: Date.now() }, { status: 200 })
}
