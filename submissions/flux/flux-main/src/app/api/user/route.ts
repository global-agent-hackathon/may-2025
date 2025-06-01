import { NextRequest, NextResponse } from 'next/server';
import { currentUser } from '@clerk/nextjs/server';
import prismadb from '@/lib/db';

// Force dynamic to avoid caching issues
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  console.log("GET /api/user - Request received");
  
  try {
    // Get the current Clerk user
    const user = await currentUser();
    console.log("Clerk user:", user?.id);
    
    if (!user) {
      console.log("No authenticated user found");
      return new NextResponse(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Find primary email
    const primaryEmail = user.emailAddresses.find(
      email => email.id === user.primaryEmailAddressId
    )?.emailAddress;

    if (!primaryEmail) {
      console.log("User doesn't have a primary email");
      return new NextResponse(JSON.stringify({ error: 'User does not have a primary email' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
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
    } else {
      console.log("Found existing user:", dbUser.id);
      
      // Update the user record if needed
      if (
        user.imageUrl !== dbUser.imageUrl ||
        (user.firstName && user.lastName && `${user.firstName} ${user.lastName}` !== dbUser.name) ||
        (user.username && !dbUser.name)
      ) {
        console.log("Updating user data");
        dbUser = await prismadb.user.update({
          where: { id: dbUser.id },
          data: {
            name: user.firstName && user.lastName 
              ? `${user.firstName} ${user.lastName}` 
              : user.username || dbUser.name,
            imageUrl: user.imageUrl,
          }
        });
        console.log("User updated");
      }
    }

    return NextResponse.json(dbUser);
  } catch (error) {
    console.error('Error in user sync:', error);
    return new NextResponse(JSON.stringify({ 
      error: 'Internal Server Error', 
      details: error instanceof Error ? error.message : String(error) 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
} 