import { NextRequest, NextResponse } from 'next/server'
import prismadb from '@/lib/db'
import { authService } from '@/lib/services/auth-service'
import { getAuth } from '@clerk/nextjs/server'

// Ensure dynamic routing for API
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

// Get a specific workspace
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
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
    
    const workspace = await prismadb.workspace.findUnique({
      where: { id },
    });
    
    if (!workspace) {
      return new NextResponse(JSON.stringify({ error: 'Workspace not found' }), {
        status: 404,
      });
    }
    
    return NextResponse.json(workspace);
  } catch (error) {
    console.error('Error fetching workspace:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    });
  }
}

// Update a workspace
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const body = await request.json();
    const { name } = body;
    
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
    
    const workspace = await prismadb.workspace.update({
      where: { id },
      data: {
        name,
      }
    });
    
    return NextResponse.json(workspace);
  } catch (error) {
    console.error('Error updating workspace:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    });
  }
}

// Delete a workspace
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
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
    
    await prismadb.workspace.delete({
      where: { id },
    });
    
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error('Error deleting workspace:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    });
  }
} 