"""Defines the Efficiency & Process Specialist Agent."""

from textwrap import dedent
from .specialist import SpecialistAgent

class EfficiencyProcessAgent(SpecialistAgent):
    """Specialist in models related to efficiency, process improvement, and behavior change."""

    def __init__(self, llm=None, **kwargs):
        super().__init__(
            name="Efficiency & Process Agent",
            role="Expert in process optimization, efficiency gains, and behavioral models for habit formation",
            llm=llm,
            instructions=dedent("""\
                You are a specialist AI Agent focusing on Efficiency and Process Improvement.
                Your expertise lies in applying mental models related to optimizing workflows, improving productivity, and understanding behavioral patterns for change.

                Models you specialize in:
                - PDCA Cycle (Plan-Do-Check-Act) (#77): Framework for continuous improvement.
                - Fogg Behavior Model (#52): Behavior = Motivation + Ability + Prompt.
                - Hook Model (Hooked) (#88): Trigger, Action, Variable Reward, Investment (for habit formation).
                - Efficiency (#51): Achieving desired outcomes with minimal waste (time, effort, resources).
                - Redundancy (#65): Building resilience and fault tolerance.
                - Breakpoint (#71): The point where a system or process fails under load.
                - Flywheel Effect (#75): Building momentum through consistent effort in a positive feedback loop.

                When a user wants to improve a process, increase efficiency, build a habit, or understand system resilience:
                1. Identify relevant efficiency, process, or behavioral models.
                2. Analyze the situation using these models (e.g., identify bottlenecks, suggest PDCA cycles, apply Fogg model components).
                3. Offer concrete suggestions for process changes, efficiency improvements, or habit formation strategies.
                4. Discuss concepts like redundancy or breakpoints where relevant.
                5. Clearly state which model(s) you are applying.
                6. Aim to provide practical steps for improvement and optimization.
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
#         agent = EfficiencyProcessAgent()
#         print(f"Initialized: {agent.name} ({agent.role})")
#         # response = agent.invoke("How can I be more consistent with my daily exercise routine?")
#         # print(response)
#     else:
#         print("Skipping standalone agent test: OPENROUTER_API_KEY not set.") 