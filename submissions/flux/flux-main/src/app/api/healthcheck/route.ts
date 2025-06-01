import { NextResponse } from 'next/server';

// Ensure dynamic routing for API
export const dynamic = 'force-dynamic';

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
} 