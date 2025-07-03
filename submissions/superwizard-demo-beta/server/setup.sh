#!/bin/bash

echo "🚀 Setting up Superwizard Server..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created! Please edit it with your OpenRouter API key."
else
    echo "ℹ️  .env file already exists."
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENROUTER_API_KEY"
echo "2. Start the database:"
echo "   docker-compose up -d pgvector"
echo "3. Start the server:"
echo "   python server.py"
echo "4. Access your server at:"
echo "   http://localhost:7777"
echo "5. View API docs at:"
echo "   http://localhost:7777/docs"
echo ""
echo "🎯 Happy automating!" 