import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    console.log(`Fetching course data for ID: ${id}`);
    
    // Fetch from Stepik API
    const response = await fetch(`https://stepik.org/api/courses/${id}`);
    
    if (!response.ok) {
      console.error(`Stepik API error: ${response.status} ${response.statusText}`);
      return NextResponse.json(
        { error: `Failed to fetch course: ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log(`Successfully fetched course data for ID: ${id}`);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching course data:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}