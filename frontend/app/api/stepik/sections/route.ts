import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const courseId = searchParams.get('course');

    if (!courseId) {
      return NextResponse.json(
        { error: 'Missing course parameter' },
        { status: 400 }
      );
    }

    const response = await fetch(`https://stepik.org/api/sections?course=${courseId}`);

    if (!response.ok) {
      return NextResponse.json(
        { error: `Failed to fetch sections: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}