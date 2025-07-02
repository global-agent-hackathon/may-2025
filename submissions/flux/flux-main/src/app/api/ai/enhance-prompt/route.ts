import { NextRequest, NextResponse } from "next/server";
import { getAuth, auth } from "@clerk/nextjs/server";
import { z } from "zod";
import { getEnhancedFormContext, extractContextualKeywords, searchMemoriesWithContext } from "@/lib/memory";

// Input validation schema
const enhancePromptRequestSchema = z.object({
  prompt: z.string().min(1, "Prompt is required"),
  userId: z.string().optional(),
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
    // Get authenticated user
    const { userId: clerkUserId } = getAuth(request);
    if (!clerkUserId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Parse and validate request body
    const body = await request.json();
    const { prompt, userId } = enhancePromptRequestSchema.parse(body);

    console.log("[ENHANCE_PROMPT] Enhancing prompt:", prompt.substring(0, 100) + "...");

    // Get memory context and insights
    let memoryContext = "";
    let contextualInsights = "";
    
    try {
      // Extract keywords for better context
      const keywords = extractContextualKeywords(prompt);
      console.log("[ENHANCE_PROMPT] Extracted keywords:", keywords);

      // Get enhanced context based on similar successful forms
      if (userId || clerkUserId) {
        const userIdToUse = userId || clerkUserId;
        memoryContext = await getEnhancedFormContext(userIdToUse, prompt);
        
        // Get specific examples of similar successful forms
        const contextMemories = await searchMemoriesWithContext(userIdToUse, prompt, 3, "form_interaction");
        if (contextMemories?.memories?.length) {
          const successfulExamples = contextMemories.memories
            .filter(m => m.metadata?.ai_form_analytics?.success_score >= 7)
            .map(m => ({
              prompt: m.metadata?.original_prompt || m.memory,
              fieldCount: m.metadata?.ai_form_analytics?.generated_field_count,
              fieldTypes: m.metadata?.ai_form_analytics?.generated_field_types
            }))
            .slice(0, 2);
          
          if (successfulExamples.length > 0) {
            contextualInsights = `Successful examples: ${successfulExamples.map(ex => 
              `"${ex.prompt}" (${ex.fieldCount} fields: ${ex.fieldTypes?.join(', ') || 'various types'})`
            ).join('; ')}`;
          }
        }
      }
    } catch (error) {
      console.warn("[ENHANCE_PROMPT] Failed to get memory context:", error);
    }

    // Prepare the request to send to the Python agent API
    const agentRequest = {
      prompt: prompt.trim(),
      context: memoryContext,
      examples: contextualInsights
    };

    console.log("[ENHANCE_PROMPT] Making request to Python agent API");
    
    // Call Python agent API to enhance the prompt
    const authHeaders = await getAuthHeaders();
    const response = await fetch(`${AGENT_API_URL}/enhance-prompt`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify(agentRequest),
    });

    console.log("[ENHANCE_PROMPT] Python agent API response status:", response.status, response.statusText);

    if (!response.ok) {
      const errorData = await response.text();
      console.error("[ENHANCE_PROMPT] Python agent API error:", errorData);
      
      // Fallback enhancement using simple rules
      const fallbackEnhanced = enhancePromptFallback(prompt, memoryContext);
      return NextResponse.json({
        enhancedPrompt: fallbackEnhanced,
        source: "fallback",
        memoryContext: memoryContext.substring(0, 200) + "...",
        improvements: ["Added specificity and context", "Applied rule-based enhancements"],
        confidence: 0.6
      });
    }

    const enhancementData = await response.json();
    console.log("[ENHANCE_PROMPT] Python agent API response:", enhancementData);

    return NextResponse.json({
      enhancedPrompt: enhancementData.enhanced_prompt || enhancementData.enhancedPrompt,
      source: "flux_agent",
      memoryContext: memoryContext.substring(0, 200) + "...",
      improvements: enhancementData.improvements || [],
      confidence: enhancementData.confidence || 0.8
    });

  } catch (error) {
    console.error("[ENHANCE_PROMPT] Error:", error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Invalid request data", details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: "Failed to enhance prompt" },
      { status: 500 }
    );
  }
}

// Fallback enhancement function using simple rules
function enhancePromptFallback(prompt: string, memoryContext: string): string {
  let enhanced = prompt.trim();
  
  // Add specificity if prompt is too short
  if (enhanced.length < 50) {
    enhanced += ". Include appropriate field types, labels, and validation rules.";
  }
  
  // Add context-based suggestions
  const lowerPrompt = enhanced.toLowerCase();
  
  if (lowerPrompt.includes('feedback') || lowerPrompt.includes('survey')) {
    enhanced += " Include rating scales (1-5 or 1-10), multiple choice questions for categories, and open-ended text fields for detailed comments.";
  }
  
  if (lowerPrompt.includes('application') || lowerPrompt.includes('job')) {
    enhanced += " Include personal information fields, experience/education sections, file upload for resume/documents, and skills assessment questions.";
  }
  
  if (lowerPrompt.includes('registration') || lowerPrompt.includes('event')) {
    enhanced += " Include date/time selection, contact information, dietary restrictions or special requirements, and payment information if needed.";
  }
  
  if (lowerPrompt.includes('contact') || lowerPrompt.includes('inquiry')) {
    enhanced += " Include name, email, phone number, subject/category selection, and a detailed message field.";
  }
  
  // Add memory insights if available
  if (memoryContext && memoryContext.length > 10) {
    enhanced += ` ${memoryContext}`;
  }
  
  return enhanced;
} 