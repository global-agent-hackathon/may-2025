import os
import sys
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables first
load_dotenv()

import uvicorn
from api.routes import app
from utils.logger import get_logger

logger = get_logger()

def main():
    """Main entry point for the application."""
    logger.info("Starting Flux Agent server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 