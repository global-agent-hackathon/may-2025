import { NextRequest, NextResponse } from "next/server";
import { getAuth } from "@clerk/nextjs/server";
import { auth } from "@clerk/nextjs/server";
import prismadb from "@/lib/db";

const FLUX_AGENT_URL = process.env.AGENT_API_URL || 'http://localhost:8000';
console.log('[Next.js API /generate-chart] Using FLUX_AGENT_URL:', FLUX_AGENT_URL);

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

// Helper to get DB userId from Clerk userId
async function getDbUserId(clerkUserId: string | null): Promise<string | null> {
  if (!clerkUserId) return null;
  
  const user = await prismadb.user.findUnique({
    where: { externalId: clerkUserId },
    select: { id: true }
  });
  
  return user?.id || null;
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;

    // Get authenticated user
    const { userId: clerkUserId } = getAuth(request);
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Get database user ID
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    const { prompt } = await request.json();
    if (!prompt || prompt.trim() === "") {
      return NextResponse.json(
        { error: "Prompt is required" },
        { status: 400 }
      );
    }

    // Verify form access and get form data
    const form = await prismadb.form.findFirst({
      where: {
        id: id,
        isDeleted: false,
        OR: [
          { userId: userId },
          { published: true }
        ]
      },
      include: {
        responses: {
          select: {
            id: true,
            data: true,
            createdAt: true
          }
        }
      }
    });

    if (!form) {
      return NextResponse.json({ error: "Form not found" }, { status: 404 });
    }

    // Parse form schema to get field information
    const schema = form.schema as any || {};
    let fields: any[] = [];
    
    // Handle both old format (array) and new format (object with fields and metadata)
    if (schema.fields && Array.isArray(schema.fields)) {
      fields = schema.fields;
    } else if (Array.isArray(schema)) {
      fields = schema;
    }

    console.log('[Next.js API /generate-chart] Attempting to call Flux Agent at:', `${FLUX_AGENT_URL}/analytics/generate-charts`);
    console.log('[Next.js API /generate-chart] Request body for Flux Agent:', JSON.stringify({
      form_id: id,
      prompt: prompt.trim(),
      context: {
        form_title: form.title,
        form_description: form.description,
        fields: fields.map((field: any) => ({
          id: field.id,
          label: field.label,
          type: field.type,
          options: field.options || []
        })),
        total_responses: form.responses.length,
        latest_response_date: form.responses.length > 0 
          ? Math.max(...form.responses.map((r: any) => new Date(r.createdAt).getTime()))
          : null
      }
    }, null, 2));

    // Call flux-agent backend for AI-powered chart generation
    const response = await fetch(`${FLUX_AGENT_URL}/analytics/generate-charts`, {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({
        form_id: id,
        prompt: prompt.trim(),
        context: {
          form_title: form.title,
          form_description: form.description,
          fields: fields.map((field: any) => ({
            id: field.id,
            label: field.label,
            type: field.type,
            options: field.options || []
          })),
          total_responses: form.responses.length,
          latest_response_date: form.responses.length > 0 
            ? Math.max(...form.responses.map((r: any) => new Date(r.createdAt).getTime()))
            : null
        }
      })
    });

    console.log('[Next.js API /generate-chart] Flux Agent response status:', response.status);

    if (!response.ok) {
      const errorData = await response.text();
      console.error('[Next.js API /generate-chart] Error from Flux Agent:', errorData);
      console.log('[Next.js API /generate-chart] Returning FALLBACK suggestions due to Flux Agent error.');
      
      // Fallback to simple chart suggestions if AI service fails
      const fallbackSuggestions = [
        {
          title: "Response Count Over Time",
          type: "line",
          description: "Shows how form responses have been submitted over time",
          config: {
            field_id: "createdAt",
            field_label: "Submission Date",
            sql_query: `SELECT DATE(created_at) as date, COUNT(*) as count 
                       FROM form_responses 
                       WHERE form_id = '${id}' 
                       GROUP BY DATE(created_at) 
                       ORDER BY date`,
            data_transform: "time_series"
          },
          confidence: 0.8
        }
      ];

      return NextResponse.json({
        prompt,
        form_id: id,
        total_responses: form.responses.length,
        available_fields: fields.map((f: any) => ({ id: f.id, label: f.label, type: f.type })),
        suggestions: fallbackSuggestions
      });
    }

    const chartSuggestions = await response.json();
    console.log('[Next.js API /generate-chart] Successfully received chart suggestions from Flux Agent:', JSON.stringify(chartSuggestions, null, 2));
    return NextResponse.json(chartSuggestions);

  } catch (error) {
    console.error("[Next.js API /generate-chart] Internal error:", error);
    return NextResponse.json(
      { error: "Failed to generate chart suggestions" },
      { status: 500 }
    );
  }
} 