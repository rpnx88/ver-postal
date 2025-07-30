
import React from 'react';
import { loadDashboardData } from '@/lib/server-data';
import DashboardClient from '@/components/dashboard-client';

// Revalidate every 60 seconds (ISR)
export const revalidate = 60;

// Force dynamic rendering to ensure fresh data
export const dynamic = 'force-dynamic';

export default async function DashboardPage() {
  let data = null;
  
  try {
    // Try to load initial data server-side for better performance
    data = await loadDashboardData();
    console.log('Server-side data loaded:', data ? 'success' : 'failed');
  } catch (error) {
    console.warn('Server-side data loading failed, will load client-side:', error);
    // Don't return error here, let client-side handle it
  }
  
  // Always render DashboardClient - it will handle loading states
  // If data is null, the client will fetch it dynamically
  return <DashboardClient initialData={data as any} />;
}
