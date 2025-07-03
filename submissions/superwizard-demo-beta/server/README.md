# Superwizard Server

AI-powered DOM automation server using Gemini 2.0 Flash for intelligent browser automation.

## 🚀 Features

- **FastAPI Web Interface**: Modern REST API interface on port 7777
- **Intelligent DOM Automation**: Natural language to browser actions
- **Multi-step Task Management**: Context-aware automation workflows
- **Persistent Memory**: Agent memory and session storage with PostgreSQL
- **Gemini 2.0 Flash**: Powered by Google's latest AI model via OpenRouter
- **Single Endpoint**: Clean, unified interface on one port

## 📁 Project Structure

```
superwizard-server/
├── agents/
│   ├── __init__.py
│   ├── superwizard_agent.py      # Main Agno agent implementation
│   └── selector.py               # Agent selection utilities
├── api/
│   ├── __init__.py
│   └── settings.py               # Configuration settings
├── db/
│   ├── __init__.py
│   ├── session.py                # Database session management
│   └── url.py                    # Database URL configuration
├── server.py                     # FastAPI server entry point
├── start.sh                      # Easy start script
├── setup.sh                      # Initial setup script
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Python dependencies
├── .env.template                 # Environment variables template
├── .env                          # Environment variables (create from template)
├── compose.yaml                  # PostgreSQL database only
└── README.md                     # This file
```

## 🛠️ Quick Start


### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- OpenRouter API key (for Gemini 2.0 Flash access)

### 1. Setup

```bash
# Run setup script
./setup.sh

# Edit .env file with your OpenRouter API key
nano .env
```

### 2. Start Everything

```bash
# Single command to start database and server
./start.sh
```

### 3. Access Your Server

Open: **http://localhost:7777**

## ⚙️ Manual Setup (Alternative)

### 1. Clone and Configure

```bash
cd superwizard-server
cp env.template .env
```

### 2. Configure Environment

Edit `.env` file with your API keys:

```bash
# Required: Get this from OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Database settings (defaults work)
DB_USER=superwizard
DB_PASSWORD=superwizard123
DB_NAME=superwizard_db
DB_HOST=localhost
DB_PORT=5433

# Server settings
SERVER_PORT=7777
DEBUG=true
TELEMETRY_ENABLED=false
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Services

```bash
# Start PostgreSQL
docker-compose up -d pgvector

# Start server
export DB_USER=superwizard && export DB_PASSWORD=superwizard123 && export DB_NAME=superwizard_db && export DB_HOST=localhost && export DB_PORT=5433 && python server.py
```

## 🧠 Agent Capabilities

The Superwizard agent is a FastAPI-powered agent that can:

- **Understand natural language instructions** for browser automation
- **Provide intelligent responses** about web automation tasks
- **Remember context** across conversations using persistent memory
- **Learn from interactions** to improve over time
- **Handle complex multi-step tasks** with reasoning capabilities

### Example Interactions

```
User: "How do I automate clicking a search button?"
Agent: "I can help you automate clicking a search button. You'll need to..."

User: "What's the best way to fill out a form automatically?"
Agent: "For automated form filling, I recommend these approaches..."
```

## 🔗 Integration

This setup uses a standalone FastAPI server, which provides:

1. **REST API**: Clean HTTP endpoints for agent interaction
2. **Session Management**: Persistent conversations and memory
3. **Real-time Responses**: Fast agent response processing
4. **Multi-user Support**: Handle multiple users simultaneously

## 📊 Database Schema

The server uses PostgreSQL with pgvector for:

- **Agent Sessions**: Persistent conversation history
- **Agent Memory**: Long-term memory storage with vector embeddings
- **User Context**: Multi-user session management

## 🐛 Development

### Project Commands

```bash
# Setup everything
./setup.sh

# Start server
./start.sh

# Start only database
docker-compose up -d pgvector

# Stop database
docker-compose down

# View database logs
docker-compose logs pgvector
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key for Gemini 2.0 | Required |
| `DB_USER` | PostgreSQL username | `superwizard` |
| `DB_PASSWORD` | PostgreSQL password | `superwizard123` |
| `DB_NAME` | PostgreSQL database name | `superwizard_db` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5433` |
| `SERVER_PORT` | Server port | `7777` |
| `DEBUG` | Enable debug mode | `true` |
| `TELEMETRY_ENABLED` | Enable telemetry | `false` |

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `./start.sh`
5. Submit a pull request

## 💡 Support

For issues and questions:

1. Check the API documentation at http://localhost:7777/docs
2. Review the agent configuration in `agents/superwizard_agent.py`
3. Check database connection with `docker-compose logs pgvector`
4. Verify the server is running on http://localhost:7777

## 🎯 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Chat Test UI   │───▶│  FastAPI Server  │───▶│ Superwizard     │
│ (chat_test.html)│    │    (port 7777)   │    │     Agent       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │                       │
                                 ▼                       ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   PostgreSQL     │    │ OpenRouter API  │
                       │   (port 5433)    │    │ (Gemini 2.0)    │
                       └──────────────────┘    └─────────────────┘
```
