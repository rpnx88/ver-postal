

'use client';

import { useState, useEffect, useCallback } from 'react';
import { DashboardData } from '@/lib/data';

interface UseDashboardDataReturn {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  lastFetch: number | null;
  refetch: () => Promise<void>;
}

export function useDashboardData(initialData?: DashboardData): UseDashboardDataReturn {
  const [data, setData] = useState<DashboardData | null>(initialData || null);
  const [loading, setLoading] = useState(!initialData);
  const [error, setError] = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<number | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching fresh dashboard data...');
      
      // Add timestamp to prevent caching
      const timestamp = Date.now();
      const response = await fetch(`/api/dashboard-data?t=${timestamp}`, {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache'
        },
        cache: 'no-store'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const freshData = await response.json();
      
      console.log('Fresh data loaded:', {
        timestamp: freshData._apiMeta?.fetchedAt,
        totalIndicacoes: freshData.metadata?.total_indicacoes
      });
      
      setData(freshData);
      setLastFetch(Date.now());
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-fetch if no initial data
  useEffect(() => {
    if (!initialData) {
      fetchData();
    }
  }, [initialData, fetchData]);

  return {
    data,
    loading,
    error,
    lastFetch,
    refetch: fetchData
  };
}
