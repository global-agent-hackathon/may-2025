import { NextResponse } from 'next/server'
import { currentUser } from '@clerk/nextjs/server'
import prisma from '@/lib/db'

// Mark as dynamic to prevent static analysis issues
export const dynamic = 'force-dynamic';

// Get favorites for a user
export async function GET() {
  try {
    // Get the current Clerk user
    const user = await currentUser();
    
    if (!user) {
      return new NextResponse("Unauthorized", { status: 401 });
    }
    
    // First, find the internal user ID from the external Clerk ID
    const dbUser = await prisma.user.findUnique({
      where: { externalId: user.id },
      select: { id: true }
    });
    
    if (!dbUser) {
      return new NextResponse("User not found", { status: 404 });
    }
    
    // Get all favorites with related form data
    const favorites = await prisma.favorite.findMany({
      where: { userId: dbUser.id },
      include: {
        user: {
          select: {
            id: true,
            name: true
          }
        }
      },
      orderBy: { createdAt: 'desc' }
    });
    
    // Manually fetch the associated forms since we don't have a direct relation
    const formIds = favorites.map(fav => fav.formId);
    
    const forms = await prisma.form.findMany({
      where: { 
        id: { in: formIds },
        isDeleted: false
      },
      select: {
        id: true,
        title: true,
        description: true,
        published: true,
        updatedAt: true,
        workspace: {
          select: {
            id: true,
            name: true
          }
        }
      }
    });
    
    // Combine the data
    const result = favorites.map(favorite => {
      const form = forms.find(f => f.id === favorite.formId);
      return {
        ...favorite,
        form
      };
    });
    
    return NextResponse.json(result);
  } catch (error) {
    console.error("[FAVORITES_GET]", error);
    return new NextResponse("Internal Error", { status: 500 });
  }
} 