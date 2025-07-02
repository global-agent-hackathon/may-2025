import { NextRequest, NextResponse } from 'next/server'
import prismadb from '@/lib/db'

// Mark as dynamic to prevent static analysis issues
export const dynamic = 'force-dynamic';

// Move a form to trash
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;
    
    if (!id) {
      return new NextResponse(JSON.stringify({ error: 'Form ID is required' }), {
        status: 400,
      })
    }
    
    const form = await prismadb.form.update({
      where: { id },
      data: { 
        isInTrash: true,
        isDeleted: true 
      }
    })
    
    return NextResponse.json(form)
  } catch (error) {
    console.error('Error moving form to trash:', error)
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    })
  }
} 