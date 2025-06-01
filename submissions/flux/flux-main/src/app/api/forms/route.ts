import { NextRequest, NextResponse } from 'next/server'
import prismadb from '@/lib/db'
import { getAuth } from '@clerk/nextjs/server'
import { authService } from '@/lib/services/auth-service'

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

// Get all forms for the authenticated user
export async function GET(request: NextRequest) {
  try {
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
    
    // Fetch forms for the user with submission counts
    const forms = await prismadb.form.findMany({
      where: { 
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
    console.error('Error fetching forms:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    });
  }
}

// Create a new form (without associating to a workspace)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    // Destructure schema from body as well
    const { title, description, schema } = body; 
    
    if (!title) {
      return new NextResponse(JSON.stringify({ error: 'Title is required' }), {
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
    
    // Create the form in the database
    const form = await prismadb.form.create({
      data: {
        title,
        description: description || "", // Add description here too
        userId,
        published: false,
        // Use the schema from the request body, default to empty array if not provided
        schema: schema || [], 
      },
    });
    
    return NextResponse.json(form);
  } catch (error) {
    console.error('Error creating form:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    });
  }
} 