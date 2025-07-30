
import { NextRequest, NextResponse } from 'next/server';
import { loadDashboardData } from '@/lib/server-data';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const data = await loadDashboardData();
    
    if (!data) {
      return NextResponse.json(
        { error: 'Failed to load dashboard data' },
        { status: 500 }
      );
    }

    // Add cache control headers to prevent stale data
    const headers = new Headers();
    headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
    headers.set('Pragma', 'no-cache');
    headers.set('Expires', '0');

    return NextResponse.json(data, { headers });
  } catch (error) {
    console.error('Error in data API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
