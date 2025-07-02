import { NextRequest, NextResponse } from "next/server";
import { getAuth } from "@clerk/nextjs/server";
import { auth } from "@clerk/nextjs/server";
import prismadb from "@/lib/db";
import { z } from "zod";

// Input validation schema
const formBuilderRequestSchema = z.object({
  prompt: z.string().min(1, "Prompt is required"),
  workspaceId: z.string().optional(),
  context: z.string().optional(),
  existingFormSchema: z.any().optional(), // Allow passing existing schema
});

// Configure Python Agent API URL
const AGENT_API_URL = process.env.AGENT_API_URL || "http://localhost:8000";

// Interface for the response from the LLM
interface FormGenerationResponse {
  title: string;
  description: string;
  fields: {
    id: string;
    type: string;
    label: string;
    placeholder?: string;
    required: boolean;
    options?: string[];
    fileSize?: number;
    fileTypes?: string[];
  }[];
}

// Helper to get DB userId from Clerk userId (defined locally)
async function getDbUserId(clerkUserId: string | null): Promise<string | null> {
  if (!clerkUserId) return null;
  
  const user = await prismadb.user.findUnique({
    where: { externalId: clerkUserId },
    select: { id: true }
  });
  
  return user?.id || null;
}

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
      return new NextResponse(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
      });
    }

    // Get database user ID (using local helper)
    const userId = await getDbUserId(clerkUserId);
    if (!userId) {
      return new NextResponse(JSON.stringify({ error: "User not found" }), {
        status: 404,
      });
    }

    // Parse and validate request body
    const body = await request.json();
    const validationResult = formBuilderRequestSchema.safeParse(body);
    
    if (!validationResult.success) {
      return new NextResponse(
        JSON.stringify({ 
          error: "Invalid request", 
          details: validationResult.error.format() 
        }),
        { status: 400 }
      );
    }

    const { prompt, workspaceId, context, existingFormSchema } = validationResult.data;
    console.log("[FORM_BUILDER] Prompt:", prompt);
    if (existingFormSchema) {
      console.log("[FORM_BUILDER] Existing Form Schema provided for edit:", JSON.stringify(existingFormSchema));
    }

    // Check workspace access if workspaceId is provided
    if (workspaceId) {
      const workspace = await prismadb.workspace.findUnique({
        where: {
          id: workspaceId,
          userId,
        },
      });

      if (!workspace) {
        return new NextResponse(
          JSON.stringify({ error: "Workspace not found or access denied" }),
          { status: 404 }
        );
      }
    }

    // Get workspace context if workspaceId is provided
    let workspaceContext = "";
    if (workspaceId) {
      const workspace = await prismadb.workspace.findUnique({
        where: {
          id: workspaceId,
        },
        select: {
          name: true,
        },
      });

      if (workspace) {
        workspaceContext = `Workspace: ${workspace.name}`;
      }
    }

    // Fetch user's previous forms to provide context
    const previousForms = await prismadb.form.findMany({
      where: {
        userId,
        workspaceId: workspaceId || undefined,
        isDeleted: false,
      },
      orderBy: {
        updatedAt: "desc",
      },
      take: 5,
      select: {
        title: true,
        description: true,
        schema: true,
      },
    });

    // Prepare context for the agent
    let enrichedContext = `
      ${workspaceContext}
      ${context || ""}
      
      User's previous forms (for general style context):
      ${previousForms.map((form: { title: string; description: string | null; schema: any }) => 
        `Title: ${form.title}
         Description: ${form.description || 'No description'}
         Schema: ${JSON.stringify(form.schema)}`
      ).join('\n\n')}
    `;

    // Prepare the request to send to the Python agent API
    const agentRequest = {
      prompt,
      context: enrichedContext,
      existingFormSchema: existingFormSchema || undefined
    };

    console.log("[FORM_BUILDER] Making request to Python agent API");
    
    // Call Python agent API to generate the form
    const authHeaders = await getAuthHeaders();
    const response = await fetch(`${AGENT_API_URL}/generate`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify(agentRequest),
    });

    // Log response status
    console.log("[FORM_BUILDER] Python agent API response status:", response.status, response.statusText);

    if (!response.ok) {
      const errorData = await response.json();
      console.error("[FORM_BUILDER] Python agent API error:", errorData);
      throw new Error(errorData.detail || "Failed to generate form");
    }

    const formData = await response.json();
    console.log("[FORM_BUILDER] Python agent API response data:", JSON.stringify(formData));

    return NextResponse.json({
      fields: formData.fields,
      title: formData.title,
      description: formData.description,
    });
    
  } catch (error) {
    console.error("[FORM_BUILDER_ERROR]", error);
    return new NextResponse(
      JSON.stringify({ 
        error: error instanceof Error ? error.message : "Internal server error" 
      }),
      { status: 500 }
    );
  }
} 