import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const courseId = url.searchParams.get('course');
    
    if (!courseId) {
      return NextResponse.json(
        { error: 'Missing course parameter' },
        { status: 400 }
      );
    }
    
    console.log(`Fetching sections for course ID: ${courseId}`);
    
    // Fetch from Stepik API
    const response = await fetch(`https://stepik.org/api/sections?course=${courseId}`);
    
    if (!response.ok) {
      console.error(`Stepik API error: ${response.status} ${response.statusText}`);
      return NextResponse.json(
        { error: `Failed to fetch sections: ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log(`Successfully fetched sections for course ID: ${courseId}`);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching sections:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}