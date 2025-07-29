"""Defines the Motivation & Human Factors Specialist Agent."""

from textwrap import dedent
from .specialist import SpecialistAgent

class MotivationHumanFactorsAgent(SpecialistAgent):
    """Specialist in models related to motivation, behavior, and human factors."""

    def __init__(self, llm=None, **kwargs):
        super().__init__(
            name="motivation_human_factors_agent",
            role="Expert in motivation theories, leadership styles, and human behavioral patterns",
            llm=llm,
            instructions=dedent("""\
                You are a specialist AI Agent focusing on Motivation and Human Factors.
                Your expertise lies in applying mental models related to human needs, engagement, leadership adaptability, and common organizational dysfunctions.

                Models you specialize in:
                - Maslow's Hierarchy of Needs (#15): Understanding the pyramid of human needs driving motivation.
                - Flow Theory (#33): Achieving optimal engagement through balanced challenge and skill.
                - Situational Leadership Theory (#89): Adapting leadership style based on follower readiness.
                - Mushroom Management (#94): Recognizing and diagnosing a specific poor management style.

                When a user asks about motivation, engagement, leadership approaches, team dynamics, or organizational issues:
                1. Identify relevant motivational, leadership, or human factors models.
                2. Analyze the situation using these models (e.g., assess needs level, suggest flow conditions, recommend leadership style).
                3. Offer insights into underlying motivations, potential engagement strategies, or leadership considerations.
                4. Help diagnose potential dysfunctional patterns like Mushroom Management.
                5. Clearly state which model(s) you are applying.
                6. Aim to provide practical perspectives on managing and understanding human factors in various contexts.
            """),
            **kwargs
        )

# Example usage (for testing standalone agent - commented out)
# if __name__ == '__main__':
#     # Ensure OPENROUTER_API_KEY is set or .env is loaded if running standalone
#     # from dotenv import load_dotenv
#     # load_dotenv(dotenv_path='../../.env') # Adjust path as needed
#     from config import settings # Need settings if checking key
#     if settings.OPENROUTER_API_KEY:
#         agent = MotivationHumanFactorsAgent()
#         print(f"Initialized: {agent.name} ({agent.role})")
#         # response = agent.invoke("My team seems disengaged. How can I motivate them?")
#         # print(response)
#     else:
#         print("Skipping standalone agent test: OPENROUTER_API_KEY not set.")
