import { type NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { useAuth } from "@clerk/nextjs";
import prisma from "@/lib/db";

// Get messages from a thread
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ threadId: string }> }
): Promise<NextResponse> {
  try {
    const { userId } = await useAuth();
    if (!userId) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    const threadId = (await params).threadId;

    // Get database user from Clerk ID
    const dbUser = await (prisma as any).user.findUnique({
      where: { externalId: userId },
    });

    if (!dbUser) {
      return new NextResponse("User not found", { status: 404 });
    }

    // Check if thread exists and belongs to user
    const thread = await (prisma as any).chatThread.findUnique({
      where: {
        id: threadId,
        userId: dbUser.id, // Use database ID
      },
    });

    if (!thread) {
      return new NextResponse("Thread not found or access denied", { status: 404 });
    }

    // Get messages
    const messages = await (prisma as any).chatMessage.findMany({
      where: {
        threadId,
      },
      orderBy: {
        createdAt: "asc",
      },
    });

    return NextResponse.json(messages);
  } catch (error: any) {
    console.error("[MESSAGES_GET] Error:", error);
    return new NextResponse(`Internal error: ${error.message}`, { status: 500 });
  }
}

// Add a message to a thread
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ threadId: string }> }
): Promise<NextResponse> {
  try {
    const { userId } = await useAuth();
    if (!userId) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    const threadId = (await params).threadId;
    const body = await request.json();
    const { content, role } = body; // content here is expected to be a plain string from client

    if (!content || typeof content !== 'string') { // Ensure content is a string before wrapping
      return new NextResponse("String content is required", { status: 400 });
    }

    // Get database user from Clerk ID
    const dbUser = await (prisma as any).user.findUnique({
      where: { externalId: userId },
    });

    if (!dbUser) {
      return new NextResponse("User not found", { status: 404 });
    }

    // Check if thread exists and belongs to user
    const thread = await (prisma as any).chatThread.findUnique({
      where: {
        id: threadId,
        userId: dbUser.id, // Use database ID
      },
      include: {
        form: true,
      },
    });

    if (!thread) {
      return new NextResponse("Thread not found or access denied", { status: 404 });
    }

    const messageContentJson = { type: "text", data: content }; // Wrap string content

    // Add message to thread
    const message = await (prisma as any).chatMessage.create({
      data: {
        content: messageContentJson,
        role: role || "user", // Default to user role
        threadId,
      },
    });

    // Update thread's updatedAt
    const updatedThread = await (prisma as any).chatThread.update({
      where: { id: threadId },
      data: { updatedAt: new Date() },
      select: {
        id: true,
        title: true,
        updatedAt: true,
      },
    });

    return NextResponse.json({
      message,
      thread: updatedThread,
    });
  } catch (error: any) {
    console.error("[MESSAGES_POST] Error:", error);
    return new NextResponse(`Internal error: ${error.message}`, { status: 500 });
  }
} 