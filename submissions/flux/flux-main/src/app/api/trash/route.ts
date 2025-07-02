import { NextResponse } from 'next/server';
import { currentUser } from '@clerk/nextjs/server';
import prisma from '@/lib/db';

// Mark as dynamic to prevent static analysis issues
export const dynamic = 'force-dynamic';

export async function GET() {
  try {
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
    
    // Get all items in trash with related workspace data
    const trashItems = await prisma.form.findMany({
      where: { 
        userId: dbUser.id,
        isInTrash: true,
        isDeleted: false
      },
      include: {
        workspace: {
          select: {
            id: true,
            name: true
          }
        }
      },
      orderBy: { updatedAt: 'desc' }
    });
    
    return NextResponse.json(trashItems);
  } catch (error) {
    console.error("[TRASH_GET]", error);
    return new NextResponse("Internal Error", { status: 500 });
  }
} 