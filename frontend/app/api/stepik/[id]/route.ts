import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const url = new URL(request.url);
    const searchParams = url.searchParams;
    
    console.log(`Fetching data for ID: ${id} with search params: ${searchParams.toString()}`);
    
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
    
    console.log(`Fetching from Stepik API: ${apiUrl}`);
    
    // Fetch from Stepik API
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      console.error(`Stepik API error: ${response.status} ${response.statusText}`);
      return NextResponse.json(
        { error: `Failed to fetch data: ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log(`Successfully fetched data for ID: ${id}`);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching data:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}