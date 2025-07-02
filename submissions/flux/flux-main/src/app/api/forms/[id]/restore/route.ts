import { NextRequest, NextResponse } from 'next/server'
import { getAuth } from '@clerk/nextjs/server'
import prisma from '@/lib/db'

// Mark as dynamic to prevent static analysis issues
export const dynamic = 'force-dynamic';

// Helper to get DB userId from Clerk userId
async function getDbUserId(clerkUserId: string | null): Promise<string | null> {
  if (!clerkUserId) return null;
  
  const user = await prisma.user.findUnique({
    where: { externalId: clerkUserId },
    select: { id: true }
  });
  
  return user?.id || null;
}

// Restore a form from trash
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;
    
    if (!id) {
      return new NextResponse(JSON.stringify({ error: 'Form ID is required' }), {
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
    
    // Check if the form exists and belongs to the user
    const form = await prisma.form.findFirst({
      where: { 
        id, 
        userId, 
        isInTrash: true,
        isDeleted: false 
      }
    });
    
    if (!form) {
      return new NextResponse(JSON.stringify({ error: 'Form not found in trash or unauthorized' }), {
        status: 404,
      });
    }
    
    // Restore the form from trash
    const updatedForm = await prisma.form.update({
      where: { id },
      data: { isInTrash: false }
    });
    
    return NextResponse.json(updatedForm);
  } catch (error) {
    console.error('Error restoring form from trash:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    });
  }
} 