'use client';

import { useState, useEffect } from 'react';

export default function TestPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('/api/stepik/178781');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
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
      <h2 className="text-xl mb-2">Course Title: {data?.courses?.[0]?.title || 'No title'}</h2>
      <div className="bg-gray-100 p-4 rounded">
        <pre className="text-sm overflow-auto">{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  );
}