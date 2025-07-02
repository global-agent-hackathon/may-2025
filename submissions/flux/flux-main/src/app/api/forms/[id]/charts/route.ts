import { NextRequest, NextResponse } from "next/server"
import { getAuth } from "@clerk/nextjs/server"
import prismadb from "@/lib/db"

// Helper to get DB userId from Clerk userId
async function getDbUserId(clerkUserId: string | null): Promise<string | null> {
  if (!clerkUserId) return null;
  
  const user = await prismadb.user.findUnique({
    where: { externalId: clerkUserId },
    select: { id: true }
  });
  
  return user?.id || null;
}

// GET /api/forms/[id]/charts - Get all charts for a form
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;

    const { userId: clerkUserId } = getAuth(request);
    
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Get database user ID
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    // First verify the user has access to this form
    const form = await prismadb.form.findFirst({
      where: {
        id: id,
        userId: userId,
        isDeleted: false,
      },
    })

    if (!form) {
      return NextResponse.json({ error: "Form not found" }, { status: 404 })
    }

    // Get all charts for this form
    const charts = await prismadb.chart.findMany({
      where: {
        formId: id,
        userId: userId,
      },
      orderBy: {
        createdAt: "desc",
      },
    })

    return NextResponse.json(charts)
  } catch (error) {
    console.error("Error fetching charts:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

// POST /api/forms/[id]/charts - Create a new chart for a form
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;

    const { userId: clerkUserId } = getAuth(request);
    
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Get database user ID
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    const formId = id
    const body = await request.json()
    const { title, type, config } = body

    if (!title || !type || !config) {
      return NextResponse.json(
        { error: "Missing required fields: title, type, config" },
        { status: 400 }
      )
    }

    // First verify the user has access to this form
    const form = await prismadb.form.findFirst({
      where: {
        id: formId,
        userId: userId,
        isDeleted: false,
      },
    })

    if (!form) {
      return NextResponse.json({ error: "Form not found" }, { status: 404 })
    }

    // Create the chart
    const chart = await prismadb.chart.create({
      data: {
        title,
        type,
        config,
        formId,
        userId,
      },
    })

    return NextResponse.json(chart, { status: 201 })
  } catch (error) {
    console.error("Error creating chart:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
} 