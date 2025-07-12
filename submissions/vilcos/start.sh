#!/bin/bash

# ANSI color codes for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display banner
echo -e "${BLUE}"
echo "╔═════════════════════════════════════════════════════════════╗"
echo "║                 VILCOS WEBSITE BUILDER                      ║"
echo "║         AI-Powered Website Template Management              ║"
echo "╚═════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for required tools
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}Error: Python 3 is required but not found${NC}"
  exit 1
fi

if ! command -v npm &> /dev/null; then
  echo -e "${RED}Error: npm is required but not found${NC}"
  exit 1
fi

# Set up Python environment
echo -e "${YELLOW}Setting up Python environment...${NC}"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
  if [ -f ".env" ]; then
    source .env
  fi
  
  if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}OPENAI_API_KEY is not set. Please enter your OpenAI API key:${NC}"
    read -r api_key
    if [ -z "$api_key" ]; then
      echo -e "${RED}No API key provided. Cannot continue.${NC}"
      exit 1
    fi
    echo "OPENAI_API_KEY=$api_key" >> .env
    export OPENAI_API_KEY=$api_key
  fi
fi

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}Installing npm dependencies...${NC}"
  npm install
fi

# Check if required files exist
if [ ! -f "vite.config.js" ] || [ ! -f "watch-templates.js" ]; then
  echo -e "${RED}Required configuration files are missing. Please restore vite.config.js and watch-templates.js${NC}"
  exit 1
fi

# Build the frontend initially
echo -e "${YELLOW}Building the frontend...${NC}"
npm run build

# Function to cleanup on exit
cleanup() {
  echo -e "${YELLOW}Stopping all processes...${NC}"
  kill $CHAINLIT_PID $VITE_PID $WATCHER_PID 2>/dev/null
  exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Start all services in background
echo -e "${GREEN}Starting services...${NC}"

# Start the template watcher first
echo -e "${YELLOW}Starting template file watcher...${NC}"
npm run watch > /tmp/watcher.log 2>&1 &
WATCHER_PID=$!

# Wait a moment for watcher to initialize
sleep 1

# Start Chainlit
echo -e "${YELLOW}Starting Chainlit AI interface...${NC}"

# Ensure JWT secret exists and set it as an environment variable
if [ ! -f "./.chainlit/.jwt_secret" ]; then
  echo -e "${YELLOW}Chainlit JWT secret missing, creating now...${NC}"
  mkdir -p .chainlit
  python3 -c "import secrets; print(secrets.token_hex(32))" > ./.chainlit/.jwt_secret
  echo -e "${GREEN}Chainlit JWT secret created!${NC}"
fi

# Export the JWT secret as an environment variable
export CHAINLIT_AUTH_SECRET=$(cat ./.chainlit/.jwt_secret)

# Start Chainlit
chainlit run app.py --port 8000 > /tmp/chainlit.log 2>&1 &
CHAINLIT_PID=$!

# Wait a moment for Chainlit to start
sleep 2

# Check if Chainlit started successfully
if ! ps -p $CHAINLIT_PID > /dev/null; then
  echo -e "${RED}Error: Chainlit failed to start. Check the logs at /tmp/chainlit.log${NC}"
  kill $WATCHER_PID
  exit 1
fi

# Start Vite in dev mode for better hot reloading
echo -e "${YELLOW}Starting website preview...${NC}"
npm run dev -- --port 3000 > /tmp/vite.log 2>&1 &
VITE_PID=$!

# Wait a moment for Vite to start
sleep 2

# Check if Vite started successfully
if ! ps -p $VITE_PID > /dev/null; then
  echo -e "${RED}Error: Website preview failed to start. Check the logs at /tmp/vite.log${NC}"
  kill $CHAINLIT_PID $WATCHER_PID
  exit 1
fi

# Success message
echo -e "${GREEN}Vilcos is now running!${NC}"
echo -e "${BLUE}➤ AI Management: http://localhost:8000${NC} (login: admin/password)"
echo -e "${BLUE}➤ Website Preview: http://localhost:3000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep the script running
echo -e "${YELLOW}Logs are being saved to /tmp/chainlit.log, /tmp/vite.log, and /tmp/watcher.log${NC}"
echo -e "To view logs in real-time, run: tail -f /tmp/chainlit.log"
echo

# Wait for any key press or Ctrl+C
while true; do
  sleep 10
done 