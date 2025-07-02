# Chat API Documentation

This document describes the request and response models for all Chat API endpoints in the Venture Insights backend.

## Chat Endpoints

### Get All Threads

**Endpoint:** `GET /chat/threads`

**Description:** Retrieves a list of chat threads for a user.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of threads to return. Default: 10, Range: 1-100.
- `offset` (integer, optional): Number of threads to skip. Default: 0, Min: 0.
- `user_id` (string, optional): Filter threads by user ID. If not provided and user is authenticated, it uses the authenticated user's email.
- `sort_by` (string, optional): Field to sort by. Options: "updated_at", "created_at". Default: "updated_at".
- `sort_order` (string, optional): Sort order. Options: "asc", "desc". Default: "desc".

**Response:**
```json
[
  {
    "id": "thread-123",
    "created_at": "2023-01-01T00:00:00.000Z",
    "updated_at": "2023-01-01T00:00:00.000Z",
    "created_by": "user@example.com",
    "last_message": {
      "content": "How can I help you today?",
      "sender": "assistant",
      "timestamp": "2023-01-01T00:00:05.000Z",
      "user_id": "user@example.com",
      "user_name": "John Doe"
    },
    "message_count": 2
  }
]
```

### Create Thread

**Endpoint:** `POST /chat/threads`

**Description:** Creates a new chat thread.

**Request Body:** None required.

**Response:**
```json
{
  "thread_id": "thread-123"
}
```

### Get Thread

**Endpoint:** `GET /chat/threads/{thread_id}`

**Description:** Retrieves a specific chat thread with all its messages.

**Path Parameters:**
- `thread_id` (string, required): The ID of the thread to retrieve.

**Response:**
```json
{
  "id": "thread-123",
  "created_at": "2023-01-01T00:00:00.000Z",
  "updated_at": "2023-01-01T00:00:00.000Z",
  "created_by": "user@example.com",
  "messages": [
    {
      "id": "msg-123",
      "content": "Hello, I need some information.",
      "sender": "user",
      "timestamp": "2023-01-01T00:00:00.000Z",
      "user_id": "user@example.com",
      "user_name": "John Doe"
    },
    {
      "id": "msg-124",
      "content": "How can I help you today?",
      "sender": "assistant",
      "timestamp": "2023-01-01T00:00:05.000Z",
      "metadata": {
        "tools": [],
        "formatted_tool_calls": [],
        "citations": [],
        "messages": [],
        "model": "gpt-4"
      }
    }
  ]
}
```

### Delete Thread

**Endpoint:** `DELETE /chat/threads/{thread_id}`

**Description:** Deletes a specific chat thread.

**Path Parameters:**
- `thread_id` (string, required): The ID of the thread to delete.

**Response:**
```json
{
  "success": true
}
```

### Add Message

**Endpoint:** `POST /chat/threads/{thread_id}/messages`

**Description:** Adds a new message to a thread and receives a response from the assistant.

**Path Parameters:**
- `thread_id` (string, required): The ID of the thread to add the message to.

**Query Parameters:**
- `stream` (boolean, optional): Whether to stream the response. Default: false.

**Request Body:**
```json
{
  "content": "What is the revenue analysis for Company XYZ?",
  "attachments": [
    {
      "id": "attachment-123"
    }
  ],
  "user_id": "user@example.com",
  "user_name": "John Doe"
}
```

**Response (non-streaming):**
```json
{
  "id": "msg-124",
  "content": "Based on our analysis, Company XYZ had revenue of $10M in 2023, which represents a 15% increase from the previous year.",
  "sender": "assistant",
  "timestamp": "2023-01-01T00:00:05.000Z",
  "metadata": {
    "tools": [],
    "formatted_tool_calls": [],
    "citations": [],
    "messages": [
      {
        "role": "user",
        "content": "What is the revenue analysis for Company XYZ?"
      },
      {
        "role": "assistant",
        "content": "Based on our analysis, Company XYZ had revenue of $10M in 2023, which represents a 15% increase from the previous year."
      }
    ],
    "model": "gpt-4"
  },
  "user_id": "user@example.com",
  "user_name": "John Doe"
}
```

**Response (streaming):**

For streaming responses, the API returns a Server-Sent Events (SSE) stream with the following format for each chunk:

```
data: {"content": "Based"}
data: {"content": " on our"}
data: {"content": " analysis, Company XYZ"}
data: {"content": " had revenue of $10M in 2023"}
data: {"content": ", which represents a 15% increase from the previous year."}
data: [DONE]
```

To consume this stream in the frontend, you can use the EventSource API or a library like SSE.js.

## Request Models

### SendMessageRequest

```typescript
interface SendMessageRequest {
  content: string;
  attachments?: Array<{ id: string }>;
  user_id?: string;  // User ID associated with the message
  user_name?: string;  // User name/display name
}
```

## Response Models

### ChatThreadWithMessages

```typescript
interface ChatThreadWithMessages {
  id: string;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  messages: MessageResponse[];
}
```

### MessageResponse

```typescript
interface MessageResponse {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: string;
  metadata?: {
    tools: any[];
    formatted_tool_calls: any[];
    citations: any[];
    messages: {
      role: string;
      content: string;
    }[];
    model: string;
  };
  user_id?: string;
  user_name?: string;
}
```

## Frontend Integration Guide

Here's how to integrate the Chat API with your frontend application:

### 1. Getting all threads

```javascript
async function getThreads(options = {}) {
  const { limit = 10, offset = 0, userId = null, sortBy = 'updated_at', sortOrder = 'desc' } = options;
  
  let url = `https://api.ventureinsights.com/chat/threads?limit=${limit}&offset=${offset}`;
  if (userId) url += `&user_id=${encodeURIComponent(userId)}`;
  url += `&sort_by=${sortBy}&sort_order=${sortOrder}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer YOUR_AUTH_TOKEN'
    }
  });
  return await response.json();
}
```

### 2. Creating a new thread

```javascript
async function createThread() {
  const response = await fetch('https://api.ventureinsights.com/chat/threads', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_AUTH_TOKEN',
      'Content-Type': 'application/json'
    }
  });
  return await response.json();
}
```

### 3. Getting a specific thread

```javascript
async function getThread(threadId) {
  const response = await fetch(`https://api.ventureinsights.com/chat/threads/${threadId}`, {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer YOUR_AUTH_TOKEN'
    }
  });
  return await response.json();
}
```

### 4. Deleting a thread

```javascript
async function deleteThread(threadId) {
  const response = await fetch(`https://api.ventureinsights.com/chat/threads/${threadId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': 'Bearer YOUR_AUTH_TOKEN'
    }
  });
  return await response.json();
}
```

### 5. Sending a message (non-streaming)

```javascript
async function sendMessage(threadId, message) {
  const response = await fetch(`https://api.ventureinsights.com/chat/threads/${threadId}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_AUTH_TOKEN',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      content: message,
      user_id: 'user@example.com',  // Optional if user is authenticated
      user_name: 'John Doe'  // Optional if user is authenticated
    })
  });
  return await response.json();
}
```

### 6. Sending a message (streaming)

```javascript
function sendMessageStreaming(threadId, message, onChunk, onDone) {
  const eventSource = new EventSource(
    `https://api.ventureinsights.com/chat/threads/${threadId}/messages?stream=true`, 
    {
      headers: {
        'Authorization': 'Bearer YOUR_AUTH_TOKEN',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: message,
        user_id: 'user@example.com',  // Optional if user is authenticated
        user_name: 'John Doe'  // Optional if user is authenticated
      })
    }
  );
  
  eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
      eventSource.close();
      if (onDone) onDone();
      return;
    }
    
    const chunk = JSON.parse(event.data);
    if (onChunk) onChunk(chunk.content);
  };
  
  eventSource.onerror = (error) => {
    console.error('EventSource error:', error);
    eventSource.close();
  };
  
  return eventSource;
}
```

This provides a complete guide for integrating with the Chat API from your frontend application.