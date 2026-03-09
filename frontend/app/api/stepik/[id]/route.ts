import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const { searchParams } = new URL(request.url);

    let apiUrl: string;

    // Determine the correct API endpoint based on the request
    if (id === 'sections') {
      const courseId = searchParams.get('course');
      if (!courseId) {
        return NextResponse.json(
          { error: 'Missing course parameter' },
          { status: 400 }
        );
      }
      apiUrl = `https://stepik.org/api/sections?course=${courseId}`;
    } else if (id === 'lessons') {
      const ids = searchParams.get('ids');
      if (!ids) {
        return NextResponse.json(
          { error: 'Missing ids parameter' },
          { status: 400 }
        );
      }
      apiUrl = `https://stepik.org/api/lessons?ids=${ids}`;
    } else if (id === 'users') {
      const ids = searchParams.get('ids');
      if (!ids) {
        return NextResponse.json(
          { error: 'Missing ids parameter' },
          { status: 400 }
        );
      }
      apiUrl = `https://stepik.org/api/users?ids=${ids}`;
    } else {
      // Default to course endpoint
      apiUrl = `https://stepik.org/api/courses/${id}`;
    }

    const response = await fetch(apiUrl);

    if (!response.ok) {
      return NextResponse.json(
        { error: `Failed to fetch data: ${response.statusText}` },
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