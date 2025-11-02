'use client';

import { useState, useEffect } from 'react';

export default function TestPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('Fetching course details for course ID 178781 via proxy');
        const response = await fetch('/api/stepik/178781');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Course details fetched via proxy:', result);
        setData(result);
      } catch (err) {
        console.error('Fetch error:', err);
        console.error('Error details:', {
          name: err instanceof Error ? err.name : 'Unknown',
          message: err instanceof Error ? err.message : 'Unknown error',
          stack: err instanceof Error ? err.stack : 'No stack trace'
        });
        setError(err instanceof Error ? `${err.name}: ${err.message}` : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="p-8">Loading course data...</div>;
  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;
  if (!data) return <div className="p-8">No data returned</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Test Page</h1>
      <h2 className="text-xl mb-2">Course Title: {data.courses?.[0]?.title || 'No title'}</h2>
      <div className="bg-gray-100 p-4 rounded">
        <pre className="text-sm overflow-auto">{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  );
}