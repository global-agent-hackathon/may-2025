import { NextRequest, NextResponse } from "next/server";
import { getAuth, auth } from "@clerk/nextjs/server";

const AGENT_API_URL = process.env.AGENT_API_URL || "http://localhost:8000";

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
  { params }: { params: Promise<{ userId: string }> }
): Promise<NextResponse> {
  try {
    // Get authenticated user
    const { userId: clerkUserId } = getAuth(request);
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { userId } = await params;
    
    const response = await fetch(`${AGENT_API_URL}/memory/user-preferences/${userId}`, {
      method: "GET",
      headers: await getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("User preferences backend error:", response.status, errorText);
      
      // Return graceful fallback instead of throwing
      return NextResponse.json({
        preferences: {},
        message: "User preferences temporarily unavailable"
      });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Get user preferences error:", error);
    
    // Return graceful fallback instead of 500 error
    return NextResponse.json({
      preferences: {},
      message: "User preferences temporarily unavailable"
    });
  }
} 