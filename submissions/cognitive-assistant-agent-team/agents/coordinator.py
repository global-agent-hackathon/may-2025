"""Defines the Coordinator Agent.

This agent manages user interaction, analyzes input, routes tasks to Specialist Agents,
synthesizes responses, and presents insights to the user.
"""

from textwrap import dedent
from agno.agent import Agent
# from agno.models.openai import OpenAIChat # No longer needed
from agno.models.openrouter import OpenRouter # Import OpenRouter model

# Import settings for default configuration
from config import settings

class CoordinatorAgent(Agent):
    """The Coordinator Agent for the Cognitive Assistant Team."""

    def __init__(self, llm=None, **kwargs):
        # Default to a configured LLM using OpenRouter settings if none is provided
        if llm is None:
            if settings.OPENROUTER_API_KEY: # Only create default if key exists
                configured_llm = OpenRouter(id=settings.DEFAULT_MODEL_ID)
            else:
                # Handle case where key is missing and no LLM was passed
                print("Warning: CoordinatorAgent created without a configured LLM or API key.")
                configured_llm = None # Or a dummy model instance
        else:
            configured_llm = llm

        super().__init__(
            name="coordinator_agent",
            role="Team Lead for Cognitive Assistant Agents",
            model=configured_llm,
            instructions=dedent("""\
                You are the Coordinator Agent (Team Lead) for a team of specialized AI assistants.
                Your primary role is to manage user interaction, analyze incoming user input
                (queries, documents, conversation context), identify potential cognitive tasks
                or areas where mental models could be beneficial, route these tasks to the
                appropriate Specialist Agents, synthesize their responses, and present cohesive,
                helpful insights back to the user.

                Key Functions:
                1.  Analyze User Input: Understand the user's context, goals, and potential cognitive needs.
                2.  Proactive Trigger Identification: Infer *when* a mental model might be useful, even if not explicitly asked for.
                3.  Task Routing: Decide which Specialist Agent(s) are best suited for the identified task based on their expertise.
                4.  Response Synthesis: Combine insights from Specialist Agents into a coherent, concise, and helpful response.
                5.  User Interaction:
                    - Present information clearly using markdown.
                    - Be suggestive: Offer potential mental models or perspectives proactively when relevant.
                    - Be transparent: Briefly mention which specialist(s) contributed or which model(s) are being applied, if appropriate.
                    - Be concise: Synthesize specialist inputs effectively, avoiding unnecessary jargon or length.
                    - Be controllable: Frame responses as suggestions or perspectives, allowing the user to guide the conversation.
            """),
            markdown=True,
            show_tool_calls=True, # Adjust as needed
            **kwargs
        )

    # Routing and synthesis are handled by the LLM based on instructions
    # and the team context provided by the agno framework.
    # The explicit analyze_input_and_trigger method is removed as it's
    # not aligned with the LLM-driven coordination approach.

# Example usage (for testing standalone agent - commented out)
# if __name__ == '__main__':
#     # Ensure OPENROUTER_API_KEY is set or .env is loaded if running standalone
#     # from dotenv import load_dotenv
#     # load_dotenv(dotenv_path='../../.env') # Adjust path as needed
#     # settings.check_api_keys()
#     if settings.OPENROUTER_API_KEY:
#         coordinator = CoordinatorAgent()
#         print(f"Initialized: {coordinator.name} ({coordinator.role})")
#         # response = coordinator.invoke("Tell me about sunk cost fallacy")
#         # print(response)
#     else:
#         print("Skipping standalone coordinator test: OPENROUTER_API_KEY not set.") 