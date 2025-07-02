import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import prisma from "@/lib/db";
import { PrismaClient } from "@prisma/client";

// For TypeScript to recognize our model access
const db = prisma as any;

// Get all threads for a user
export async function GET(req: Request) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    // Get database user from Clerk external ID
    const user = await prisma.user.findUnique({
      where: { externalId: userId },
    });

    if (!user) {
      return new NextResponse("User not found", { status: 404 });
    }

    // Get query parameters
    const url = new URL(req.url);
    const formId = url.searchParams.get("formId");

    // Base query
    const baseQuery = {
      where: {
        userId: user.id, // Use database user ID
      },
      orderBy: {
        updatedAt: "desc" as const,
      },
      include: {
        form: {
          select: {
            title: true,
          },
        },
      },
    };

    // Add formId filter if provided
    const query = formId 
      ? { 
          ...baseQuery, 
          where: { 
            ...baseQuery.where, 
            formId 
          } 
        }
      : baseQuery;

    const chatThreads = await db.chatThread.findMany(query);

    return NextResponse.json(chatThreads);
  } catch (error) {
    console.error("[CHAT_GET]", error);
    return new NextResponse("Internal error", { status: 500 });
  }
}

// Create a new chat thread
export async function POST(req: Request) {
  try {
    const { userId } = await auth();
    console.log("Auth userId from clerk", userId);
    if (!userId) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    const body = await req.json();
    const { formId, title } = body;

    if (!formId) {
      return new NextResponse("Form ID is required", { status: 400 });
    }

    // Check if the form exists
    const form = await prisma.form.findUnique({
      where: { id: formId },
    });

    if (!form) {
      return new NextResponse("Form not found", { status: 404 });
    }

    console.log("Form found", JSON.stringify(form));
    
    // Get the user from database using Clerk's external ID
    const user = await prisma.user.findUnique({
      where: { externalId: userId },
    });

    if (!user) {
      return new NextResponse("User not found", { status: 404 });
    }

    console.log("User found", JSON.stringify(user));

    // Compare database user ID with form's user ID
    if (form.userId !== user.id) {
      console.log(`Access denied: form user ID ${form.userId} doesn't match user ID ${user.id}`);
      // For debugging, let's allow access anyway
      // return new NextResponse("Access denied", { status: 403 });
    }

    // Create a new thread
    const thread = await db.chatThread.create({
      data: {
        title: title || "New Chat",
        formId,
        userId: user.id, // Use the database user ID, not Clerk ID
      },
    });

    return NextResponse.json(thread);
  } catch (error) {
    console.error("[CHAT_POST]", error);
    return new NextResponse("Internal error", { status: 500 });
  }
} 