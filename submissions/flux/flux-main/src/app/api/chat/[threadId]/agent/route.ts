import { type NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import prisma from "@/lib/db";
import { trackFormInteractionServer } from "@/lib/memory-server";

// Define content block types
interface TextContentBlock {
  type: "text";
  text: string;
}

interface CSVContentBlock {
  type: "csv";
  data: string;
  description?: string;
}

type ContentBlock = TextContentBlock | CSVContentBlock;

// Agent API URL from environment variables
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

// Send a message to the agent and get a response
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ threadId: string }> }
): Promise<NextResponse> {
  try {
    const { userId } = await auth();
    if (!userId) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    const threadId = (await params).threadId;
    const body = await request.json();
    const { message } = body;

    if (!message) {
      return new NextResponse("Message is required", { status: 400 });
    }

    const dbUser = await (prisma as any).user.findUnique({
      where: { externalId: userId },
    });

    if (!dbUser) {
      return new NextResponse("User not found", { status: 404 });
    }

    const thread = await (prisma as any).chatThread.findUnique({
      where: {
        id: threadId,
        userId: dbUser.id,
      },
      include: {
        form: {
          include: {
            responses: {
              orderBy: {
                createdAt: "desc",
              },
              take: 1,
            },
          },
        },
      },
    });

    if (!thread) {
      return new NextResponse("Thread not found or access denied", { status: 404 });
    }

    // Get the latest form response for this form
    const latestResponse = thread.form.responses[0];
    if (!latestResponse) {
      return new NextResponse("No form responses found for this form", { status: 404 });
    }

    const chatHistory = await (prisma as any).chatMessage.findMany({
      where: {
        threadId,
      },
      orderBy: {
        createdAt: "asc",
      },
      select: {
        id: true,
        content: true,
        role: true,
        createdAt: true,
      },
    });
    console.log(
      `[${threadId}] Fetched chatHistory for agent call (length ${chatHistory.length}):`,
      JSON.stringify(
        chatHistory.map((m: any) => {
          const contentString = typeof m.content === 'string' ? m.content : JSON.stringify(m.content);
          return { id: m.id, role: m.role, content: contentString.substring(0,20) + "...", createdAt: m.createdAt };
        })
      )
    );

    const userMessage = await (prisma as any).chatMessage.create({
      data: {
        content: { 
          content_blocks: [
            { type: "text", text: message }
          ]
        },
        role: "user",
        threadId,
      },
    });
    console.log(`[${threadId}] Stored current userMessage (id: ${userMessage.id}): ${message.substring(0,20)}...`);

    const formattedHistoryForAgent = chatHistory.map((msg: { role: string, content: any }) => {
      // Extract text content from potentially complex content structure
      let contentText = "";
      if (typeof msg.content === 'string') {
        contentText = msg.content;
      } else if (msg.content && typeof msg.content === 'object') {
        // Handle content_blocks format
        if (msg.content.content_blocks && Array.isArray(msg.content.content_blocks)) {
          // Extract text from text blocks
          const textBlocks = msg.content.content_blocks
            .filter((block: any): block is TextContentBlock => block.type === 'text');
          if (textBlocks.length > 0) {
            contentText = textBlocks.map((block: TextContentBlock) => block.text).join('\n');
          }
        } 
        // Handle legacy formats
        else if (msg.content.type === 'text') {
          contentText = msg.content.text || msg.content.data || "";
        }
      }

      return {
        role: msg.role,
        content: contentText,
      };
    });

    try {
      console.log(
        `[${threadId}] Sending to agent. Current message: "${message.substring(0,20)}...". History (length ${formattedHistoryForAgent.length}):`,
        JSON.stringify(
          formattedHistoryForAgent.map((m: any) => {
            const contentString = typeof m.content === 'string' ? m.content : JSON.stringify(m.content);
            return { role: m.role, content: contentString.substring(0,20) + "..." };
          })
        )
      );
      const response = await fetch(`${AGENT_API_URL}/chat`, {
        method: "POST",
        headers: await getAuthHeaders(),
        body: JSON.stringify({
          threadId,
          formId: thread.form.id,
          formConfig: thread.form,
          formResponse: latestResponse.data,
          message,
          history: formattedHistoryForAgent,
          userId: userId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[${threadId}] Agent API error: ${errorText}`);
        throw new Error(`Agent API returned ${response.status}: ${errorText}`);
      }

      const agentResponse = await response.json();
      console.log(`[${threadId}] Received agent response content preview:`, typeof agentResponse.content === 'string' ? agentResponse.content.substring(0,70)+"..." : "[Structured JSON content]");

      let assistantMessageContent: any;

      // Handle content_blocks if they exist in the response
      if (agentResponse.content_blocks && Array.isArray(agentResponse.content_blocks)) {
        // If the agent sends content_blocks, use those directly
        assistantMessageContent = { content_blocks: agentResponse.content_blocks };
      } 
      // Check if csv_data exists (for backward compatibility with first version of content blocks)
      else if (agentResponse.csv_data) {
        // Get the text content from the response
        const textContent = typeof agentResponse.content === 'string' 
          ? agentResponse.content 
          : (agentResponse.content?.text || agentResponse.content?.data || "");

        assistantMessageContent = { 
          content_blocks: [
            { type: "text", text: textContent },
            { 
              type: "csv", 
              data: agentResponse.csv_data,
              description: "Table with complete results"
            }
          ]
        };
      }
      // Handle string or object content
      else if (typeof agentResponse.content === 'string') {
        // If agent sends plain text, wrap it in content blocks
        assistantMessageContent = { 
          content_blocks: [
            { type: "text", text: agentResponse.content }
          ]
        };
      } else if (typeof agentResponse.content === 'object' && agentResponse.content !== null) {
        // If the content is an object but not in content_blocks format, convert it
        if (agentResponse.content.content_blocks) {
          // If it already has content_blocks, use them directly
          assistantMessageContent = agentResponse.content;
        } else {
          // Convert legacy format to content_blocks
          assistantMessageContent = { 
            content_blocks: [
              { 
                type: "text", 
                text: agentResponse.content.text || agentResponse.content.data || JSON.stringify(agentResponse.content)
              }
            ]
          };
        }
      } else {
        // Fallback for unexpected content types (null, undefined, etc.)
        assistantMessageContent = { 
          content_blocks: [
            { 
              type: "text", 
              text: "Received an empty or unexpected response from the assistant." 
            }
          ]
        };
      }

      const assistantMessage = await (prisma as any).chatMessage.create({
        data: {
          content: assistantMessageContent,
          role: "assistant",
          threadId,
        },
      });

      // Track form interaction in memory
      try {
        await trackFormInteractionServer(
          userId,
          thread.form.id,
          thread.form.title || "Untitled Form",
          "analyzed",
          {
            thread_id: threadId,
            message_preview: message.substring(0, 100),
            response_type: agentResponse.content_blocks ? "structured" : "text"
          }
        );
      } catch (memoryError) {
        console.warn("Failed to track form interaction in memory:", memoryError);
      }

      // If this is the first assistant response, generate a better thread title
      let updatedThread = thread;
      if (thread.title === "New Chat" || thread.title.startsWith("New Chat")) {
        const generatedTitle = message.length > 50 ? message.substring(0, 47) + "..." : message;
        updatedThread = await (prisma as any).chatThread.update({
          where: { id: threadId },
          data: { title: generatedTitle, updatedAt: new Date() },
        });
      } else {
        await (prisma as any).chatThread.update({
          where: { id: threadId },
          data: { updatedAt: new Date() },
        });
      }

      return NextResponse.json({
        userMessage,
        assistantMessage,
        updatedThread,
        sourceQuery: agentResponse.sourceQuery,
      });
    } catch (error: any) {
      console.error(`[AGENT_API_ERROR] AGENT_API_ERROR:`, error);
      return NextResponse.json(
        {
          userMessage,
          error: `Failed to get response from agent: ${error.message}`,
        },
        { status: 500 }
      );
    }
  } catch (error: any) {
    console.error(`AGENT_POST Error:`, error);
    return new NextResponse(`Internal error: ${error.message}`, { status: 500 });
  }
} 