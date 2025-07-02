import { NextRequest, NextResponse } from "next/server";
import { getAuth } from "@clerk/nextjs/server";
import { auth } from "@clerk/nextjs/server";
import prismadb from "@/lib/db";
import { getDbUserId } from "@/lib/auth-service";

const FLUX_AGENT_URL = process.env.AGENT_API_URL || 'http://localhost:8000';

// Helper to get auth headers for backend requests
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    const { getToken } = await auth();
    const token = await getToken();
    
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  } catch (error) {
    console.warn("Failed to get auth token:", error);
    return {
      "Content-Type": "application/json",
    };
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;

    return NextResponse.json({ 
      message: "Chart execution endpoint is working", 
      formId: id,
      timestamp: new Date().toISOString() 
    });
  } catch (error) {
    console.error("Error in GET:", error);
    return NextResponse.json(
      { error: "Failed to process request" },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;
    const { userId: clerkUserId } = getAuth(request);
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { chartConfig } = await request.json();
    if (!chartConfig || !chartConfig.sql_query) {
      return NextResponse.json(
        { error: "Chart configuration with SQL query is required" },
        { status: 400 }
      );
    }

    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    const form = await prismadb.form.findFirst({
      where: {
        id: id,
        userId: userId
      }
    });

    if (!form) {
      return NextResponse.json({ error: "Form not found" }, { status: 404 });
    }

    // Call flux-agent backend for chart execution
    const response = await fetch(`${FLUX_AGENT_URL}/analytics/execute-chart`, {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({
        form_id: id,
        chart_config: chartConfig
      })
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('Flux-agent chart execution error:', errorData);
      
      return NextResponse.json(
        { error: "Failed to execute chart query" },
        { status: 500 }
      );
    }

    const chartData = await response.json();
    
    // Ensure the response matches what ChartDisplay expects
    return NextResponse.json({
      data_points: chartData.data_points || [],
      total_points: chartData.total_points || 0,
      query_executed: chartData.query_executed,
      success: true,
      message: "Chart data retrieved successfully"
    });

  } catch (error) {
    console.error("Chart execution error:", error);
    return NextResponse.json(
      { error: "Failed to execute chart" },
      { status: 500 }
    );
  }
} 