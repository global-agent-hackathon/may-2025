# AdGenius - Python Backend

This is the backend for the AdGenius application, built with FastAPI.

## Setup

1. Install the dependencies:
```bash
# Using pip
pip install -e .

# Using uv (faster)
uv pip install -e .
```

2. Run the server:
```bash
uvicorn backend.app:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API Endpoints

- `GET /` - API welcome message
- `POST /analyze-requirement` - Analyze ad requirements
- `POST /generate-creative` - Generate ad creative
- `POST /publish-campaign` - Publish a campaign
- `GET /campaigns` - Get all campaigns
- `GET /campaign/{campaign_id}` - Get a specific campaign
- `GET /campaign-metrics/{campaign_id}` - Get metrics for a campaign

## Chat Assistant API

- `POST /chat/message` - Send a message to the chat assistant
- `GET /chat/stream/{conversation_id}` - Stream responses using SSE
- `GET /chat/conversations` - List all conversations
- `GET /chat/conversations/{conversation_id}` - Get conversation details
- `DELETE /chat/conversations/{conversation_id}` - Delete a conversation
