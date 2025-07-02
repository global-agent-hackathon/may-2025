import { NextRequest, NextResponse } from 'next/server'
import prismadb from '@/lib/db'
import { currentUser } from '@clerk/nextjs/server'

// Mark as dynamic to prevent static analysis issues and caching
export const dynamic = 'force-dynamic';

// Helper to get DB userId from Clerk
async function getOrCreateDbUser(): Promise<string | null> {
  try {
    // Get the current Clerk user
    const user = await currentUser();
    
    if (!user) {
      console.log("No authenticated user found");
      return null;
    }

    // Find primary email
    const primaryEmail = user.emailAddresses.find(
      (email: { id: string, emailAddress: string }) => email.id === user.primaryEmailAddressId
    )?.emailAddress;

    if (!primaryEmail) {
      console.log("User doesn't have a primary email");
      return null;
    }

    // Check if we already have this user in our database
    console.log("Looking for user with externalId:", user.id);
    let dbUser = await prismadb.user.findUnique({
      where: { externalId: user.id },
    });

    // If not, create a new user record
    if (!dbUser) {
      console.log("Creating new user in database");
      dbUser = await prismadb.user.create({
        data: {
          externalId: user.id,
          email: primaryEmail,
          name: user.firstName && user.lastName 
            ? `${user.firstName} ${user.lastName}` 
            : user.username || '',
          imageUrl: user.imageUrl,
        }
      });
      console.log("Created user:", dbUser.id);
    }

    return dbUser.id;
  } catch (error) {
    console.error("Error getting or creating user:", error);
    return null;
  }
}

// Create a new workspace
export async function POST(request: NextRequest) {
  console.log("POST /api/workspace - Request received");
  
  try {
    const body = await request.json();
    console.log("Request body:", body);
    
    const { name } = body;
    
    if (!name) {
      console.log("Missing name parameter");
      return new NextResponse(JSON.stringify({ error: 'Workspace name is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Get or create database user ID
    const userId = await getOrCreateDbUser();
    console.log("Database userId:", userId);
    
    if (!userId) {
      console.log("User not found or could not be created");
      return new NextResponse(JSON.stringify({ error: 'User not found or could not be created' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log("Creating workspace with name:", name, "and userId:", userId);
    const workspace = await prismadb.workspace.create({
      data: {
        name,
        userId,
      }
    });
    
    console.log("Workspace created successfully:", workspace);
    return NextResponse.json(workspace);
  } catch (error) {
    console.error('Error creating workspace:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error', details: error instanceof Error ? error.message : String(error) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Get all workspaces for a user
export async function GET(request: NextRequest) {
  console.log("GET /api/workspace - Request received");
  
  try {
    // Get or create database user ID
    const userId = await getOrCreateDbUser();
    console.log("Database userId:", userId);
    
    if (!userId) {
      console.log("User not found or could not be created");
      return new NextResponse(JSON.stringify({ error: 'User not found or could not be created' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log("Fetching workspaces for userId:", userId);
    const workspaces = await prismadb.workspace.findMany({
      where: { userId },
      orderBy: { updatedAt: 'desc' },
    });
    
    console.log("Workspaces fetched successfully, count:", workspaces.length);
    return NextResponse.json(workspaces);
  } catch (error) {
    console.error('Error fetching workspaces:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error', details: error instanceof Error ? error.message : String(error) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
} 