import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

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

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${AGENT_API_URL}/memory/user-preference`, {
      method: "POST",
      headers: await getAuthHeaders(),
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Add user preference memory error:", error);
    return NextResponse.json(
      { error: "Failed to add user preference memory" },
      { status: 500 }
    );
  }
} 