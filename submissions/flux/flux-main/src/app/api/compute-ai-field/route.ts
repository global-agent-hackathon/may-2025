import { NextRequest, NextResponse } from 'next/server'
import { auth } from "@clerk/nextjs/server"

// Helper to get auth headers for backend requests
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    const { getToken } = await auth()
    const token = await getToken()
    
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  } catch (error) {
    console.warn("Failed to get auth token:", error)
    return {
      "Content-Type": "application/json",
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { ai_field_id, ai_metadata_prompt, form_data } = body

    if (!ai_metadata_prompt) {
      return NextResponse.json(
        { error: 'ai_metadata_prompt is required' },
        { status: 400 }
      )
    }

    if (!ai_field_id) {
      return NextResponse.json(
        { error: 'ai_field_id is required' },
        { status: 400 }
      )
    }

    // Call the flux-agent backend to compute the AI field value
    const agentResponse = await fetch(`${process.env.AGENT_API_URL}/compute-ai-field`, {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({
        ai_field_id,
        ai_metadata_prompt,
        form_data: form_data || {}
      }),
    })

    if (!agentResponse.ok) {
      const errorText = await agentResponse.text()
      console.error('Flux agent error:', errorText)
      return NextResponse.json(
        { error: 'Failed to compute AI field value' },
        { status: 500 }
      )
    }

    const result = await agentResponse.json()
    return NextResponse.json(result)

  } catch (error) {
    console.error('Error in compute-ai-field API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 