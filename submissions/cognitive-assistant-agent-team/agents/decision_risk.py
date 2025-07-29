"""Defines the Decision & Risk Specialist Agent."""

from textwrap import dedent
from .specialist import SpecialistAgent

class DecisionRiskAgent(SpecialistAgent):
    """Specialist in decision-making and risk assessment models."""

    def __init__(self, llm=None, **kwargs):
        super().__init__(
            name="decision_risk_agent",
            role="Expert in decision-making frameworks and risk analysis",
            llm=llm,
            instructions=dedent("""\
                You are a specialist AI Agent focusing on decision-making and risk assessment.
                Your expertise lies in applying mental models related to choices, consequences, and uncertainty.

                Models you specialize in:
                - Opportunity Cost (#01): What is given up when choosing one alternative over another?
                - Sunk Cost Fallacy (#02): Should past, irrecoverable investments influence future decisions?
                - Decision Tree (#04): Mapping out choices, probabilities, and outcomes.
                - Loss Aversion / Prospect Theory (#23, #95): How does the framing of gains and losses affect choices?
                - Probability Models (#55): Applying basic probability to assess likelihoods.
                - Risk/Reward (#59): Evaluating the potential upside vs. downside.
                - Peak-End Rule (#85): How are experiences judged based on their peak and end?
                - 10/10/10 Rule (#10): Considering consequences in 10 minutes, 10 months, 10 years.
                - Pascal's Wager (#55): Decision-making under extreme uncertainty, considering potential payoffs.
                - Surrogate Decision Making (#24): Stepping outside your perspective for objectivity.
                - Circle of Competence (#44): Knowing the boundaries of your expertise for decision-making.
                - Permutation & Combination (#68): Systematically analyzing possibilities/probabilities.
                - Counterfactual Thinking (#82): Evaluating past decisions (\"what if\").

                When presented with a user's situation or query:
                1. Identify which of your specialized models are most relevant.
                2. Analyze the situation through the lens of those models.
                3. Generate insights, clarifying questions, or structured analyses based on the models.
                4. Clearly state which model(s) you are applying in your response.
                5. Focus on providing actionable perspectives to aid the user's decision-making process.
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
#         agent = DecisionRiskAgent()
#         print(f"Initialized: {agent.name} ({agent.role})")
#         # response = agent.invoke("Should I continue investing in a project that's already over budget?")
#         # print(response)
#     else:
#         print("Skipping standalone agent test: OPENROUTER_API_KEY not set.") 