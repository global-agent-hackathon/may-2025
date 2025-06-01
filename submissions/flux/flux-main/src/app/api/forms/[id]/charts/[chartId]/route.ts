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

// GET /api/forms/[id]/charts/[chartId] - Get a specific chart
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; chartId: string }> }
): Promise<NextResponse> {
  try {
    const { id, chartId } = await params;

    const { userId: clerkUserId } = getAuth(request);
    
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Get database user ID
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    const chart = await prismadb.chart.findFirst({
      where: {
        id: chartId,
        formId: id,
        userId: userId,
      },
    })

    if (!chart) {
      return NextResponse.json({ error: "Chart not found" }, { status: 404 })
    }

    return NextResponse.json(chart)
  } catch (error) {
    console.error("Error fetching chart:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

// PUT /api/forms/[id]/charts/[chartId] - Update a specific chart
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; chartId: string }> }
) {
  try {
    const { id, chartId } = await params;

    const { userId: clerkUserId } = getAuth(request);
    
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Get database user ID
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    const body = await request.json()
    const { title, type, config } = body

    // Verify chart exists and user has access
    const existingChart = await prismadb.chart.findFirst({
      where: {
        id: chartId,
        formId: id,
        userId: userId,
      },
    })

    if (!existingChart) {
      return NextResponse.json({ error: "Chart not found" }, { status: 404 })
    }

    // Update the chart
    const updatedChart = await prismadb.chart.update({
      where: {
        id: chartId,
      },
      data: {
        ...(title && { title }),
        ...(type && { type }),
        ...(config && { config }),
      },
    })

    return NextResponse.json(updatedChart)
  } catch (error) {
    console.error("Error updating chart:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

// DELETE /api/forms/[id]/charts/[chartId] - Delete a specific chart
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; chartId: string }> }
): Promise<NextResponse> {
  try {
    const { id, chartId } = await params;

    const { userId: clerkUserId } = getAuth(request);
    
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Get database user ID
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    // Verify chart exists and user has access
    const existingChart = await prismadb.chart.findFirst({
      where: {
        id: chartId,
        formId: id,
        userId: userId,
      },
    })

    if (!existingChart) {
      return NextResponse.json({ error: "Chart not found" }, { status: 404 })
    }

    // Delete the chart
    await prismadb.chart.delete({
      where: {
        id: chartId,
      },
    })

    return NextResponse.json({ message: "Chart deleted successfully" })
  } catch (error) {
    console.error("Error deleting chart:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
} 