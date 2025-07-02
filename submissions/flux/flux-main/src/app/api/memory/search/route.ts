import { NextRequest, NextResponse } from "next/server";
import { getAuth, auth } from "@clerk/nextjs/server";
import { z } from "zod"; // Add zod for validation

const AGENT_API_URL = process.env.AGENT_API_URL || "http://localhost:8000";

// Input validation schema
const searchRequestSchema = z.object({
  user_id: z.string().optional(),
  query: z.string().min(1, "Search query cannot be empty"),
  limit: z.number().optional(),
  memory_type: z.string().optional(),
});

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
    // Get authenticated user
    const { userId: clerkUserId } = getAuth(request);
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Parse request body
    const body = await request.json();
    console.log("Memory search request body:", JSON.stringify(body));
    
    // Validate request and ensure query is not empty
    try {
      const validatedData = searchRequestSchema.parse({
        ...body,
        user_id: body.user_id || clerkUserId,
      });
      
      // Make the request to the backend API
      const response = await fetch(`${AGENT_API_URL}/memory/search`, {
        method: "POST",
        headers: await getAuthHeaders(),
        body: JSON.stringify(validatedData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Memory search backend error:", response.status, errorText);
        
        // Return a graceful fallback instead of throwing
        return NextResponse.json({
          memories: [],
          total_count: 0,
          message: "Memory search temporarily unavailable"
        });
      }

      const data = await response.json();
      return NextResponse.json(data);
      
    } catch (validationError) {
      console.error("Memory search validation error:", validationError);
      
      // If validation fails, use a default query of "recent" to avoid the blank query error
      if (body.query === undefined || body.query === null || body.query.trim() === "") {
        console.log("Empty query detected, using default query 'recent'");
        
        const fallbackQuery = {
          user_id: body.user_id || clerkUserId,
          query: "recent", // Default non-empty query
          limit: body.limit || 10,
          memory_type: body.memory_type,
        };
        
        // Try with the fallback query
        const response = await fetch(`${AGENT_API_URL}/memory/search`, {
          method: "POST",
          headers: await getAuthHeaders(),
          body: JSON.stringify(fallbackQuery),
        });
        
        if (response.ok) {
          const data = await response.json();
          return NextResponse.json(data);
        }
      }
      
      // If fallback fails or there's another validation error, return a 400 with clear message
      return NextResponse.json(
        { 
          error: "Invalid search parameters", 
          details: "The 'query' field cannot be empty",
          memories: [],
          total_count: 0 
        }, 
        { status: 400 }
      );
    }
    
  } catch (error) {
    console.error("Memory search error:", error);
    
    // Return graceful fallback instead of 500 error
    return NextResponse.json({
      memories: [],
      total_count: 0,
      message: "Memory search temporarily unavailable"
    });
  }
} 