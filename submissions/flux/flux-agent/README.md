# Flux Agent API

A professional, intelligent API for dynamic form generation and data analysis using AI agents.

## Features

- **Intelligent Form Generation**: Create dynamic forms from natural language prompts
- **AI Field Computation**: Automatically compute field values using AI analysis
- **Text-to-SQL Analysis**: Natural language querying of form submission data
- **Web Content Integration**: Scrape and analyze web content for form enhancement
- **Clean Architecture**: Modular, maintainable codebase with proper separation of concerns

## Architecture

```
flux-agent/
├── src/
│   ├── api/           # FastAPI routes and endpoints
│   ├── services/      # Business logic and AI orchestration
│   ├── utils/         # Shared utilities and helpers
│   ├── models.py      # Pydantic models and schemas
│   └── main.py        # Application entry point
├── app/               # Legacy code (being phased out)
├── requirements.txt   # Python dependencies
└── .env.example       # Environment variables template
```

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Required API keys (see Environment Variables)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flux-agent
```

2. **Quick setup (recommended):**
```bash
make setup
source venv/bin/activate
```

**OR manual setup:**

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
make install
# OR manually: pip3 install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:

**Development mode (with auto-reload):**
```bash
make run-dev
```

**Production mode:**
```bash
make run
# OR manually: python3 -m src.main
```

The API will be available at `http://localhost:8000`

### Available Make Commands

- `make setup` - Create virtual environment and install all dependencies
- `make install` - Install all dependencies (assumes venv is activated)
- `make run` - Run the application in production mode
- `make run-dev` - Run the application in development mode with auto-reload

## Environment Variables

Create a `.env` file with the following variables:

```env
# API Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development

# AI Service API Keys
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Logging
LOG_LEVEL=INFO
```

## API Endpoints

### Form Generation
- `POST /generate` - Generate a form from natural language prompt
- `POST /compute-ai-field` - Compute AI field values

### Data Analysis
- `POST /chat` - Natural language querying of form data

### Health Check
- `GET /health` - Service health status

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Generate a Form

```python
import requests

response = requests.post("http://localhost:8000/generate", json={
    "prompt": "Create a customer feedback form for a restaurant",
    "context": "We need to collect ratings and comments about food quality"
})

form_schema = response.json()
```

### Compute AI Field

```python
response = requests.post("http://localhost:8000/compute-ai-field", json={
    "ai_field_id": "sentiment_analysis",
    "ai_metadata_prompt": "Analyze the sentiment of the feedback",
    "form_data": {
        "field_data": {"feedback": "The food was amazing!"},
        "form_fields": [{"id": "feedback", "label": "Customer Feedback"}]
    }
})

result = response.json()
```

### Chat with Data

```python
response = requests.post("http://localhost:8000/chat", json={
    "threadId": "thread_123",
    "formId": "form_456",
    "message": "What's the average rating for our restaurant?",
    "history": [],
    "formConfig": {...},
    "formResponse": {...}
})

chat_response = response.json()
```

## Development

### Code Structure

- **Services**: Business logic and AI orchestration
  - `FormService`: Handles form generation and AI field computation
  - `TextToSQLService`: Manages data analysis and SQL generation

- **Utils**: Shared utilities
  - `DatabaseService`: Database operations
  - `DataProcessor`: Data cleaning and transformation
  - `Logger`: Structured logging

- **Models**: Pydantic schemas for request/response validation

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "src.main"]
```

### Production Considerations

- Use a production WSGI server (Gunicorn)
- Set up proper logging and monitoring
- Configure database connection pooling
- Implement rate limiting
- Set up SSL/TLS termination

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For questions and support, please [create an issue](link-to-issues) or contact the development team. 