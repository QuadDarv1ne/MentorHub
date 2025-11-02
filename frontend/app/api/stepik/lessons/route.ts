import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const ids = url.searchParams.get('ids');
    
    if (!ids) {
      return NextResponse.json(
        { error: 'Missing ids parameter' },
        { status: 400 }
      );
    }
    
    console.log(`Fetching lessons for IDs: ${ids}`);
    
    // Fetch from Stepik API
    const response = await fetch(`https://stepik.org/api/lessons?ids=${ids}`);
    
    if (!response.ok) {
      console.error(`Stepik API error: ${response.status} ${response.statusText}`);
      return NextResponse.json(
        { error: `Failed to fetch lessons: ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log(`Successfully fetched lessons for IDs: ${ids}`);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching lessons:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}