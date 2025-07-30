

import { NextRequest, NextResponse } from 'next/server';
import { loadDashboardData } from '@/lib/server-data';

// Force dynamic rendering to ensure fresh data
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('Dashboard data API called at:', new Date().toISOString());
    
    const data = await loadDashboardData();
    
    if (!data) {
      return NextResponse.json(
        { error: 'Failed to load dashboard data' },
        { status: 500 }
      );
    }

    // Add timestamp for version tracking
    const dataWithTimestamp = {
      ...data,
      _apiMeta: {
        fetchedAt: Date.now(),
        version: Date.now().toString()
      }
    };

    // Aggressive cache control headers for production
    const headers = new Headers();
    headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
    headers.set('Pragma', 'no-cache');
    headers.set('Expires', '0');
    headers.set('Surrogate-Control', 'no-store');
    headers.set('X-Accel-Expires', '0');
    
    // Add custom header to force fresh data
    headers.set('X-Data-Fresh', 'true');
    
    console.log('Returning fresh dashboard data with timestamp:', dataWithTimestamp._apiMeta.fetchedAt);

    return NextResponse.json(dataWithTimestamp, { 
      status: 200,
      headers 
    });
  } catch (error) {
    console.error('Error in dashboard-data API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
