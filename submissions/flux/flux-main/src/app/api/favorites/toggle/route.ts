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
    const { formId } = body;
    
    if (!formId) {
      return new NextResponse("Form ID is required", { status: 400 });
    }
    
    // First, find the internal user ID from the external Clerk ID
    const dbUser = await prisma.user.findUnique({
      where: { externalId: user.id },
      select: { id: true }
    });
    
    if (!dbUser) {
      return new NextResponse("User not found", { status: 404 });
    }
    
    // Check if the form exists
    const form = await prisma.form.findUnique({
      where: { 
        id: formId,
        isDeleted: false 
      }
    });
    
    if (!form) {
      return new NextResponse("Form not found", { status: 404 });
    }
    
    // Check if already favorited
    const existingFavorite = await prisma.favorite.findFirst({
      where: {
        userId: dbUser.id,
        formId: formId
      }
    });
    
    let favorite;
    let action;
    
    if (existingFavorite) {
      // Remove from favorites
      favorite = await prisma.favorite.delete({
        where: { id: existingFavorite.id }
      });
      action = 'removed';
    } else {
      // Add to favorites
      favorite = await prisma.favorite.create({
        data: {
          userId: dbUser.id,
          formId: formId
        }
      });
      action = 'added';
    }
    
    return NextResponse.json({ success: true, action, favorite });
  } catch (error) {
    console.error("[FAVORITES_TOGGLE]", error);
    return new NextResponse("Internal Error", { status: 500 });
  }
} 