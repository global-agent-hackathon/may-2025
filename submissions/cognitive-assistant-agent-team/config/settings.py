"""Configuration settings for the agent team."""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
# This is useful for local development.
load_dotenv()

# --- LLM Configuration (Using OpenRouter) ---

# Attempt to get the OpenRouter API key from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1" # Default OpenRouter API base

# You could add other configurations here, e.g.:
# - API keys for other services (e.g., search tools)
# - Logging settings

# Default model ID (using a model available on OpenRouter)
# See https://openrouter.ai/docs#models for available models
DEFAULT_MODEL_ID = "openai/gpt-4.1-mini" # Or specify like openrouter/anthropic/claude-3-haiku

# --- Validation ---

def check_api_keys():
    """Checks if essential API keys are configured."""
    if not OPENROUTER_API_KEY:
        print("----------------------------------------------------------------------")
        print("Warning: OPENROUTER_API_KEY environment variable is not set.")
        print("The application needs access to OpenRouter.")
        print("Please set it in your environment or create a .env file.")
        print("Example .env file content:")
        print("OPENROUTER_API_KEY='your_openrouter_api_key_here'")
        print("----------------------------------------------------------------------")
        # Depending on requirements, you might want to raise an error here
        raise ValueError("OPENROUTER_API_KEY is not configured.")

# You might call check_api_keys() when the application starts
check_api_keys() 