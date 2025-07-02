from linkedin_api import Linkedin
import os
import json
import requests
from dotenv import load_dotenv
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from typing import List, Optional
from pydantic import BaseModel, Field
import time
import random
import logging
load_dotenv(dotenv_path="./env", verbose=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define Pydantic model for structured output
class EditedChatMessage(BaseModel):
    edited_message: str = Field(..., description="The revised version of the input message, reflecting the requested edits.")
OPENAI_API_KEY=""

logger.info("Initializing profile_analyzer agent...")
profile_analyzer = Agent(
    model=OpenAIChat(id="gpt-4o-mini", api_key=OPENAI_API_KEY),
    instructions=[
        "You are an AI assistant specializing in text editing.",
        "Given an original message and an editing request, you will provide the revised message.",
        "Ensure the output strictly adheres to the requested edits."
    ],
    response_model=EditedChatMessage,
    markdown=True
)
logger.info("profile_analyzer agent initialized successfully")

# Function to handle message editing
def edit_message(original_msg, edit_req):
    logger.info(f"edit_message called with: original_msg={original_msg[:30]}..., edit_req={edit_req[:30]}...")
    try:
        # Construct a clear prompt for the agent
        prompt_to_edit = f"""Original Message:
'''{original_msg}'''

Edit Request:
'''{edit_req}'''

Please provide the edited message.
"""
        logger.info("Calling profile_analyzer.run...")
        # Run the agent
        response_data = profile_analyzer.run(prompt_to_edit)
        logger.info("profile_analyzer.run completed successfully")
        edited_message = response_data.content.edited_message
        logger.info(f"Edited message: {edited_message[:30]}...")
        return edited_message
    except Exception as e:
        logger.error(f"Error in edit_message: {str(e)}", exc_info=True)
        raise

# For standalone testing
if __name__ == '__main__':
    # Example usage
    logger.info("Running standalone test...")
    original_msg = "Ths is a smple msg with errrs."
    edit_req = "Please fix all spelling and grammar mistakes."
    
    try:
        edited = edit_message(original_msg, edit_req)
        print(f"Original: {original_msg}")
        print(f"Edit Request: {edit_req}")
        print(f"Edited: {edited}")
        logger.info("Standalone test completed successfully")
    except Exception as e:
        logger.error(f"Error in standalone test: {str(e)}", exc_info=True)