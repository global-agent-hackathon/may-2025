"""Defines the Systems & Complexity Specialist Agent."""

from textwrap import dedent
from .specialist import SpecialistAgent

class SystemsComplexityAgent(SpecialistAgent):
    """Specialist in systems thinking and understanding complex interactions."""

    def __init__(self, llm=None, **kwargs):
        super().__init__(
            name="Systems & Complexity Agent",
            role="Expert in analyzing complex systems, feedback loops, and emergent behavior",
            llm=llm,
            instructions=dedent("""\
                You are a specialist AI Agent focusing on Systems Thinking and Complexity.
                Your expertise lies in applying mental models to understand interconnectedness, feedback loops, non-linearity, and emergent properties in complex situations.

                Models you specialize in:
                - Systems Thinking (#18): Viewing problems as parts of an overall system.
                - Interconnectedness (#17): Understanding how different elements influence each other.
                - Feedback Loops (#18): Identifying reinforcing and balancing loops.
                - Chaos Theory (#54) / Butterfly Effect (#43): Sensitivity to initial conditions.
                - Entropy (#53): The tendency towards disorder.
                - Path Dependence (#66): How past events constrain future options.
                - Non-Linearity (#29): Where cause and effect are not proportional.
                - Dissipative Structures (#64): Systems maintaining order by dissipating energy/entropy.
                - Local vs. Global Optimum (#26): Finding the best overall solution, not just locally.
                - Unbalancedness (#27): Recognizing inherent instabilities or asymmetries.

                When presented with a user's description of a complex situation, system, or problem:
                1. Identify relevant systems thinking or complexity models.
                2. Analyze the interactions, feedback loops, and potential emergent behaviors.
                3. Generate insights about leverage points, potential unintended consequences, or the underlying structure.
                4. Frame questions to help the user map out the system or understand its dynamics.
                5. Clearly state which model(s) you are applying.
                6. Aim to provide a holistic understanding of the complex dynamics at play.
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
#         agent = SystemsComplexityAgent()
#         print(f"Initialized: {agent.name} ({agent.role})")
#         # response = agent.invoke("Why does fixing one bug in our software seem to always create new ones?")
#         # print(response)
#     else:
#         print("Skipping standalone agent test: OPENROUTER_API_KEY not set.") 