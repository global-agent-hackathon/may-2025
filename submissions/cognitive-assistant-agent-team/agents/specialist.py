"""Defines the base class for Specialist Agents."""

from textwrap import dedent
from agno.agent import Agent
# from agno.models.openai import OpenAIChat # No longer needed
from agno.models.openrouter import OpenRouter # Import OpenRouter model
from config import settings

# LLM configuration is handled by passing an instance during creation
# or using the default configured via settings if llm=None is passed.

# DEFAULT_LLM = OpenAIChat(id="gpt-4o") # Old default

class SpecialistAgent(Agent):
    """Base class for Specialist Agents in the Cognitive Assistant Team."""

    def __init__(self, name: str, role: str, instructions: str, llm=None, **kwargs):
        # Default to a configured LLM using OpenRouter settings if none is provided
        if llm is None:
            if settings.OPENROUTER_API_KEY: # Only create default if key exists
                # Explicitly pass API key here too
                configured_llm = OpenRouter(
                    id=settings.DEFAULT_MODEL_ID,
                    api_key=settings.OPENROUTER_API_KEY
                )
            else:
                # Handle case where key is missing and no LLM was passed
                # Option 1: Raise error
                # raise ValueError("OpenRouter API Key is missing and no LLM provided.")
                # Option 2: Use a dummy/placeholder or print warning (current choice)
                print("Warning: SpecialistAgent created without a configured LLM or API key.")
                configured_llm = None # Or a dummy model instance
        else:
            configured_llm = llm

        super().__init__(
            name=name,
            role=role,
            model=configured_llm,
            instructions=instructions,
            markdown=True,
            show_tool_calls=True, # Adjust as needed
            **kwargs
        )
        # Specialist agents might not need direct access to complex tools initially,
        # their expertise is primarily encoded in their instructions and LLM interaction.
        # Tools can be added later if needed (e.g., for data retrieval, calculations). 