# AdGenius Chat Assistant

This package implements the AI chat assistant feature for AdGenius, powered by the Agno agent framework with AWS Bedrock.

## Components

- **Agent:** The core chat agent implementation using AWS Bedrock Claude model
- **Tools:** Domain-specific tools for ad campaign creation and optimization
- **Storage:** Persistent storage for chat history using SQLite

## Features

- **Memory & Persistence:** Conversation history is stored in both SQLite database and Agno's native storage
- **Ad Campaign Tools:** Specialized tools for ad audience analysis, budget calculation, and ad copy suggestions
- **Reasoning:** Includes reasoning tools to provide transparent thinking processes to users
- **SSE Streaming:** Supports Server-Sent Events for real-time streaming responses

## Architecture

The chat assistant is structured as follows:

1. **User Interface Layer:** React-based UI with event streaming support (see `src/components/AIChat.tsx`)
2. **API Layer:** FastAPI endpoints for message submission and streaming responses (see `backend/chat_assistant/routes.py`)
3. **Agent Layer:** Agno agent with AWS Bedrock integration (this package)
4. **Storage Layer:** 
   - `backend/utils/db.py` - Main conversation storage for UI retrieval
   - Agno's native SQLiteStorage - Agent memory storage

## Usage

```python
# Create chat agent instance for a conversation
agent = ChatAgent(conversation_id="conv-123", user_id="user-456")

# Process a message with streaming
async for chunk in agent.process_message("How can I create a TikTok ad campaign for my fitness app?"):
    print(chunk, end="", flush=True)
```

## Available Tools

### Reasoning Tool
Allows the agent to show its reasoning process for complex topics.

### Ad Campaign Tools

1. **Audience Analysis:**
   - Analyzes target audience options for products in specific regions
   - Suggests appropriate targeting parameters

2. **Budget Calculator:**
   - Calculates optimal budget allocation across platforms
   - Provides estimated impressions and performance metrics

3. **Ad Copy Suggestions:**
   - Generates platform-specific ad copy templates
   - Provides best practices for creative content

## Configuration

The chat assistant uses AWS Bedrock and requires the following environment variables:

- `AWS_ACCESS_KEY_ID`: AWS access key with Bedrock permissions
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: us-east-1)

Storage configuration:
- SQLite storage file location: `backend/tmp/agents.db`

## Dependencies

All dependencies are managed via the project's `pyproject.toml` file. The main dependencies for this module are:

- `agno>=1.4.0`: Agno Agent framework
- `boto3>=1.29.0`: AWS SDK for Python
- `sse-starlette>=1.6.5`: Server-Sent Events for FastAPI/Starlette

To install dependencies, use:

```bash
# From the project root
uv run pip install -e .
```

## Data Storage Changes

As of the latest update, the chat assistant uses a streamlined data storage approach:

### JSON Event Data Storage

Instead of storing individual fields (role, content, tool_calls, tool_results) separately, we now store the entire event data as a single JSON object in the `data` column. This approach has several benefits:

- **Schema Flexibility**: Adding new event properties doesn't require database schema changes
- **Complete Context**: The entire event context is preserved for debugging and analysis
- **Simplified Serialization**: Removes the need for multiple serialization/deserialization steps
- **Future-proof**: Automatically supports any new fields introduced in future models

The `MessageTable` schema is now simplified to:

```python
class MessageTable(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    data = Column(Text, nullable=False)  # Stores the full JSON event data
    created_at = Column(DateTime, nullable=False)
```

### UUID Generation

We use UUID5 (name-based, SHA-1 hash) for generating both conversation and message IDs:

- **Deterministic**: The same inputs produce the same UUIDs, aiding in debugging and testing
- **Namespaced**: We use different namespace UUIDs for conversations vs. messages
- **Standard Format**: Clean UUID format without prefixes or custom formatting

### SQLAlchemy ORM

All database operations now use SQLAlchemy ORM with proper async/await patterns:

- **Async First**: All repository methods are async and use SQLAlchemy's async API
- **Session-based**: Database sessions are passed to repository methods via dependency injection
- **Clean Interface**: Repository methods have clear, typed interfaces for improved safety

## Testing

The changes to the chat assistant are thoroughly tested with unit tests. To run the tests:

```bash
pytest backend/chat_assistant/test_repository.py -v
```

The test suite includes:

- Basic CRUD operations for conversations and messages
- Verification of UUID5 deterministic generation
- Testing complex JSON event data serialization and deserialization
- Edge case handling and error conditions

These tests ensure that the new storage approach correctly preserves all event data, including nested structures, arrays, and various data types. 

