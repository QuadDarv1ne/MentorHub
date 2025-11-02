'use client';

import { useState, useEffect } from 'react';
import { getCourseDetails } from '@/lib/api/stepik';

export default function TestPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        console.log('Fetching course details for course ID 178781');
        const result = await getCourseDetails(178781);
        console.log('Course details fetched:', result);
        setData(result);
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data</div>;

  return (
    <div>
      <h1>Test Page</h1>
      <h2>Course Title: {data.title}</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}