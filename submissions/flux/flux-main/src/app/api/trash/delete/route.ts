import { NextRequest, NextResponse } from 'next/server';
import { currentUser } from '@clerk/nextjs/server';
import prisma from '@/lib/db';

// Mark as dynamic to prevent static analysis issues
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const user = await currentUser();
    
    if (!user) {
      return new NextResponse("Unauthorized", { status: 401 });
    }
    
    const body = await req.json();
    const { formId, emptyTrash } = body;
    
    // First, find the internal user ID from the external Clerk ID
    const dbUser = await prisma.user.findUnique({
      where: { externalId: user.id },
      select: { id: true }
    });
    
    if (!dbUser) {
      return new NextResponse("User not found", { status: 404 });
    }
    
    if (emptyTrash) {
      // Empty the entire trash
      const result = await prisma.form.updateMany({
        where: { 
          userId: dbUser.id,
          isInTrash: true,
          isDeleted: false
        },
        data: { 
          isDeleted: true,
          deletedAt: new Date()
        }
      });
      
      return NextResponse.json({ 
        success: true, 
        message: "Trash emptied",
        count: result.count
      });
    } else if (formId) {
      // Delete a specific form permanently
      // Check if the form exists, is in trash, and belongs to the user
      const form = await prisma.form.findFirst({
        where: { 
          id: formId,
          userId: dbUser.id,
          isInTrash: true,
          isDeleted: false
        }
      });
      
      if (!form) {
        return new NextResponse("Form not found in trash or unauthorized", { status: 404 });
      }
      
      // Mark the form as deleted
      const updatedForm = await prisma.form.update({
        where: { id: formId },
        data: { 
          isDeleted: true,
          deletedAt: new Date()
        }
      });
      
      return NextResponse.json({ 
        success: true, 
        message: "Form permanently deleted",
        form: updatedForm
      });
    } else {
      return new NextResponse("Either formId or emptyTrash parameter is required", { status: 400 });
    }
  } catch (error) {
    console.error("[TRASH_DELETE]", error);
    return new NextResponse("Internal Error", { status: 500 });
  }
} 