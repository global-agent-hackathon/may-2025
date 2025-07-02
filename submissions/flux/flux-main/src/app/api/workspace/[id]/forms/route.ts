import { NextRequest, NextResponse } from 'next/server'
import prismadb from '@/lib/db'
import { authService } from '@/lib/services/auth-service'
import { getAuth } from '@clerk/nextjs/server'

// Mark as dynamic to prevent static analysis issues
export const dynamic = 'force-dynamic';

// Helper to get DB userId from Clerk userId
async function getDbUserId(clerkUserId: string | null): Promise<string | null> {
  if (!clerkUserId) return null;
  
  const user = await prismadb.user.findUnique({
    where: { externalId: clerkUserId },
    select: { id: true }
  });
  
  return user?.id || null;
}

// Get forms for a specific workspace
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;
    
    if (!id) {
      return new NextResponse(JSON.stringify({ error: 'Workspace ID is required' }), {
        status: 400,
      });
    }
    
    // Get authenticated user
    const { userId: clerkUserId } = getAuth(request);
    if (!clerkUserId) {
      return new NextResponse(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
      });
    }
    
    // Get database user ID
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return new NextResponse(JSON.stringify({ error: 'User not found' }), {
        status: 404,
      });
    }
    
    // Verify user has access to this workspace
    const hasAccess = await authService.verifyWorkspaceAccess(id, userId);
    if (!hasAccess) {
      return new NextResponse(JSON.stringify({ error: 'Unauthorized access to workspace' }), {
        status: 403,
      });
    }
    
    const forms = await prismadb.form.findMany({
      where: { 
        workspaceId: id, 
        userId,
        isDeleted: false,
      },
      include: {
        _count: {
          select: {
            responses: true
          }
        }
      },
      orderBy: { updatedAt: 'desc' },
    });
    
    // Transform the data to include submissionCount at the top level
    const formsWithSubmissionCounts = forms.map(form => ({
      ...form,
      submissionCount: form._count.responses,
      _count: undefined // Remove the _count object from the response
    }));
    
    return NextResponse.json(formsWithSubmissionCounts, {
      headers: {
        'Cache-Control': 'public, max-age=10, stale-while-revalidate=60',
      }
    });
  } catch (error) {
    console.error('Error fetching workspace forms:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    });
  }
}

// Create a new form in a workspace
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;
    const body = await request.json();
    const { title, description, schema } = body;
    
    if (!id || !title) {
      return new NextResponse(JSON.stringify({ error: 'Missing required fields' }), {
        status: 400,
      });
    }
    
    // Get authenticated user
    const { userId: clerkUserId } = getAuth(request);
    if (!clerkUserId) {
      return new NextResponse(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
      });
    }
    
    // Get database user ID
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return new NextResponse(JSON.stringify({ error: 'User not found' }), {
        status: 404,
      });
    }
    
    // Verify user has access to this workspace
    const hasAccess = await authService.verifyWorkspaceAccess(id, userId);
    if (!hasAccess) {
      return new NextResponse(JSON.stringify({ error: 'Unauthorized access to workspace' }), {
        status: 403,
      });
    }
    
    const form = await prismadb.form.create({
      data: {
        title,
        description: description || '',
        userId,
        workspaceId: id,
        schema: schema || [],
        isDeleted: false,
      }
    });
    
    return NextResponse.json(form);
  } catch (error) {
    console.error('Error creating form:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    });
  }
} 