'use client';

import { useEffect, useState } from 'react';

export default function TestPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('[Test Page] Fetching data...');
    
    // Test direct fetch
    fetch('http://localhost:8000/api/stats')
      .then(res => {
        console.log('[Test Page] Response status:', res.status);
        return res.json();
      })
      .then(data => {
        console.log('[Test Page] Data:', data);
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('[Test Page] Error:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">API Test Page</h1>
      
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}
      {data && (
        <div className="space-y-4">
          <div className="bg-green-100 p-4 rounded">
            <h2 className="font-bold">✓ API Connection Working!</h2>
            <p>Total Events: {data.total_events}</p>
            <p>Active Alerts: {data.active_alerts}</p>
            <p>Average Sentiment: {data.average_sentiment}</p>
          </div>
          
          <details className="bg-gray-100 p-4 rounded">
            <summary className="cursor-pointer font-bold">Raw Response</summary>
            <pre className="mt-2 text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>
          </details>
        </div>
      )}
    </div>
  );
}
