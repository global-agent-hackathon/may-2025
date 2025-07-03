import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.replicate import ReplicateTools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get the API key from environment variables
replicate_api_key = os.environ.get("REPLICATE_API_TOKEN")

# Create specialized video agent
"""Create an agent specialized for Replicate AI content generation"""

video_agent = Agent(
    name="Video Creator Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[ReplicateTools(model="kwaivgi/kling-v1.6-standard")],
    description="You are an AI agent that can generate Videos using the Replicate API.",
    instructions=[
        "When the user asks you to create an video, use the `generate_media` tool to create the video.",
        "Return the URL as raw to the user.",
        "Don't convert image URL to markdown or anything else.",
    ],
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
)

video_agent.print_response("Generate an video of a nft in the dessert.")