#!/bin/bash

echo "🚀 Starting Superwizard Server..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please run ./setup.sh first."
    exit 1
fi

# Load environment variables
source .env

# Check if OpenRouter API key is set
if [ -z "$OPENROUTER_API_KEY" ] || [ "$OPENROUTER_API_KEY" = "your_openrouter_api_key_here" ]; then
    echo "❌ Please set your OPENROUTER_API_KEY in .env file"
    exit 1
fi

# Start PostgreSQL database
echo "🗄️  Starting PostgreSQL database..."
docker-compose up -d pgvector

# Wait a moment for database to start
echo "⏳ Waiting for database to start..."
sleep 3

# Set database environment variables and start server
echo "🎯 Starting Superwizard server on port 7777..."
echo ""
echo "🌐 Access your server at:"
echo "   http://localhost:7777"
echo ""
echo "📊 API docs available at:"
echo "   http://localhost:7777/docs"
echo ""

export DB_USER=superwizard
export DB_PASSWORD=superwizard123
export DB_NAME=superwizard_db
export DB_HOST=localhost
export DB_PORT=5433

python server.py 