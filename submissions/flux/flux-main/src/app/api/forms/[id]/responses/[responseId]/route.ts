import { NextRequest, NextResponse } from 'next/server'
import prismadb from '@/lib/db'

// This endpoint is dynamic and will be server-rendered
export const dynamic = 'force-dynamic';

// Get a specific response by ID
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string, responseId: string }> }
): Promise<NextResponse> {
  try {
    const { id, responseId } = await params;
    
    if (!id || !responseId) {
      return new NextResponse(JSON.stringify({ error: 'Form ID and Response ID are required' }), {
        status: 400,
      })
    }
    
    const response = await prismadb.formResponse.findUnique({
      where: { 
        id: responseId,
        formId: id
      },
    })
    
    if (!response) {
      return new NextResponse(JSON.stringify({ error: 'Response not found' }), {
        status: 404,
      })
    }
    
    return NextResponse.json(response)
  } catch (error) {
    console.error('Error fetching form response:', error)
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    })
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string, responseId: string }> }
): Promise<NextResponse> {
  try {
    const { id, responseId } = await params;
    
    if (!id || !responseId) {
      return new NextResponse(JSON.stringify({ error: 'Form ID and Response ID are required' }), {
        status: 400,
      })
    }
    
    const response = await prismadb.formResponse.findUnique({
      where: { 
        id: responseId,
        formId: id
      },
    })
    
    if (!response) {
      return new NextResponse(JSON.stringify({ error: 'Response not found' }), {
        status: 404,
      })
    }
    
    await prismadb.formResponse.delete({
      where: {
        id: responseId,
        formId: id
      },
    })
    
    return NextResponse.json({ message: 'Response deleted successfully' })
  } catch (error) {
    console.error('Error deleting form response:', error)
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    })
  }
} 