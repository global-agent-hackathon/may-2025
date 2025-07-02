import { NextRequest, NextResponse } from "next/server";
import { getAuth, auth } from "@clerk/nextjs/server";
import { z } from "zod";
import { extractContextualKeywords } from "@/lib/memory";
import { getEnhancedFormContextServer, searchMemoriesWithContextServer } from "@/lib/memory-server";

// Input validation schema
const memoryEnhanceRequestSchema = z.object({
  prompt: z.string().min(1, "Prompt is required"),
  userId: z.string().optional(), // Make userId optional since we use clerkUserId
});

// Configure Python Agent API URL
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
    console.log("[API_MEMORY_ENHANCE] Received enhance-prompt-memory request");
    
    // Get authenticated user
    const { userId: clerkUserId } = getAuth(request);
    console.log("[API_MEMORY_ENHANCE] Authenticated with Clerk user ID:", clerkUserId);
    
    if (!clerkUserId) {
      console.error("[API_MEMORY_ENHANCE] Unauthorized - no Clerk user ID");
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Parse and validate request body
    const body = await request.json();
    console.log("[API_MEMORY_ENHANCE] Request body:", JSON.stringify(body));
    
    try {
      // Get prompt from request but use the authenticated clerkUserId
      const { prompt } = memoryEnhanceRequestSchema.parse({
        ...body,
        userId: clerkUserId // Override userId with authenticated clerkUserId
      });
      console.log("[API_MEMORY_ENHANCE] Using Clerk userId:", clerkUserId);
      
      console.log("[API_MEMORY_ENHANCE] Enhancing prompt with memory:", prompt.substring(0, 100) + "...");

      // Get memory context and successful examples
      let memoryContext = "";
      let successfulExamples = "";
      
      try {
        // Extract keywords for better context
        const keywords = extractContextualKeywords(prompt);
        console.log("[MEMORY_ENHANCE] Extracted keywords:", keywords);

        // Get enhanced context based on similar successful forms - using SERVER version
        memoryContext = await getEnhancedFormContextServer(clerkUserId, prompt);
        
        // Get specific examples of similar successful forms - using SERVER version
        const contextMemories = await searchMemoriesWithContextServer(clerkUserId, prompt, 5, "form_interaction");
        if (contextMemories?.memories?.length) {
          const successfulForms = contextMemories.memories
            .filter((m: any) => m.metadata?.ai_form_analytics?.success_score >= 7)
            .map((m: any) => ({
              prompt: m.metadata?.original_prompt || m.memory,
              fieldCount: m.metadata?.ai_form_analytics?.generated_field_count,
              fieldTypes: m.metadata?.ai_form_analytics?.generated_field_types,
              score: m.metadata?.ai_form_analytics?.success_score
            }))
            .slice(0, 3);
          
          if (successfulForms.length > 0) {
            successfulExamples = successfulForms.map((form: any) => 
              `"${form.prompt}" (${form.fieldCount} fields: ${form.fieldTypes?.join(', ') || 'various'}, score: ${form.score}/10)`
            ).join('; ');
          }
        }
      } catch (error) {
        console.warn("[MEMORY_ENHANCE] Failed to get memory context:", error);
      }

      // If no memory insights found, provide helpful message
      if (!memoryContext && !successfulExamples) {
        return NextResponse.json({
          enhancedPrompt: prompt,
          source: "no_memory",
          improvements: ["No memory patterns available - create more forms to build up patterns"],
          confidence: 0.5,
          memoryInsights: "No successful form patterns found in memory",
          successfulPatterns: []
        });
      }

      // Prepare the request to send to the Python agent API
      const agentRequest = {
        prompt: prompt.trim(),
        user_id: clerkUserId, // Use clerkUserId directly 
        memory_context: memoryContext,
        successful_examples: successfulExamples
      };

      console.log("[MEMORY_ENHANCE] Making request to Python agent API");
      
      // Call Python agent API to enhance the prompt with memory
      const authHeaders = await getAuthHeaders();
      const response = await fetch(`${AGENT_API_URL}/enhance-prompt-memory`, {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify(agentRequest),
      });

      console.log("[MEMORY_ENHANCE] Python agent API response status:", response.status, response.statusText);

      if (!response.ok) {
        const errorData = await response.text();
        console.error("[MEMORY_ENHANCE] Python agent API error:", errorData);
        
        // Fallback enhancement using memory data
        const fallbackEnhanced = enhancePromptWithMemoryFallback(prompt, memoryContext, successfulExamples);
        return NextResponse.json({
          enhancedPrompt: fallbackEnhanced,
          source: "fallback",
          improvements: ["Applied memory-based fallback enhancements"],
          confidence: 0.6,
          memoryInsights: memoryContext.substring(0, 200) + "...",
          successfulPatterns: successfulExamples ? [successfulExamples.substring(0, 200) + "..."] : []
        });
      }

      const enhancementData = await response.json();
      console.log("[MEMORY_ENHANCE] Python agent API response:", enhancementData);

      return NextResponse.json({
        enhancedPrompt: enhancementData.enhanced_prompt,
        source: "memory_agent",
        improvements: enhancementData.improvements || [],
        confidence: enhancementData.confidence || 0.8,
        memoryInsights: enhancementData.memory_insights || "Memory patterns applied",
        successfulPatterns: enhancementData.successful_patterns || []
      });

    } catch (validationError) {
      console.error("[API_MEMORY_ENHANCE] Validation error:", validationError);
      return NextResponse.json(
        { error: "Invalid request data", details: validationError },
        { status: 400 }
      );
    }

  } catch (error) {
    console.error("[MEMORY_ENHANCE] Error:", error);
    
    return NextResponse.json(
      { error: "Failed to enhance prompt with memory" },
      { status: 500 }
    );
  }
}

// Fallback enhancement function using memory data
function enhancePromptWithMemoryFallback(prompt: string, memoryContext: string, successfulExamples: string): string {
  let enhanced = prompt.trim();
  
  // Add memory context if available
  if (memoryContext && memoryContext.length > 10) {
    enhanced += `. Based on your previous successful forms: ${memoryContext}`;
  }
  
  // Add successful examples insights
  if (successfulExamples && successfulExamples.length > 10) {
    enhanced += `. Consider these successful patterns: ${successfulExamples}`;
  }
  
  // Add general memory-based improvements if no specific context
  if (!memoryContext && !successfulExamples) {
    enhanced += ". To build better memory patterns, consider including specific field types, validation requirements, and user experience details.";
  }
  
  return enhanced;
} 