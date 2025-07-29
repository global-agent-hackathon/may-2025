# Main entry point for the Cognitive Assistant Agent Team

import os
from textwrap import dedent
from agno.team.team import Team
from agno.models.openrouter import OpenRouter # Use the OpenRouter model class
from pydantic import BaseModel, Field # Add pydantic imports
from agno.tools.reasoning import ReasoningTools
# Import config and agents
from config import settings
from agents import (
    CoordinatorAgent,
    DecisionRiskAgent,
    ProblemSolvingInnovationAgent,
    SystemsComplexityAgent,
    BiasPsychologyAgent,
    StrategyCompetitionAgent,
    LearningCommunicationAgent,
    EfficiencyProcessAgent,
    MotivationHumanFactorsAgent,
)

# Check API Keys on startup
settings.check_api_keys()

# Initialize the LLM using the OpenRouter class and model ID from settings
# Explicitly pass the API key as automatic detection might be failing.
llm = OpenRouter(
    id=settings.DEFAULT_MODEL_ID,
    api_key=settings.OPENROUTER_API_KEY # Explicitly pass the key
)

# == Tool Definition for Agent Delegation == (REMOVED)
# class DelegateTaskInput(BaseModel):
#     """Input schema for the delegate_to_specialist tool."""
#     agent_name: str = Field(..., description="The exact name of the specialist agent to delegate the task to (e.g., 'decision_risk_agent', 'problem_solving_innovation_agent').")
#     task_description: str = Field(..., description="The specific question or sub-task for the specialist agent.")

def create_agent_team() -> Team:
    """Instantiates all agents and assembles them into a Team."""
    coordinator = CoordinatorAgent(llm=llm)
    specialists = {
        # Use agent names as keys for potential lookup if needed, though
        # the explicit tools below are the primary delegation mechanism.
        "decision_risk_agent": DecisionRiskAgent(llm=llm),
        "problem_solving_innovation_agent": ProblemSolvingInnovationAgent(llm=llm),
        "systems_complexity_agent": SystemsComplexityAgent(llm=llm),
        "bias_psychology_agent": BiasPsychologyAgent(llm=llm),
        "strategy_competition_agent": StrategyCompetitionAgent(llm=llm),
        "learning_communication_agent": LearningCommunicationAgent(llm=llm),
        "efficiency_process_agent": EfficiencyProcessAgent(llm=llm),
        "motivation_human_factors_agent": MotivationHumanFactorsAgent(llm=llm),
    }

    all_members = [coordinator] + list(specialists.values())

    # Define the delegation tool function (REMOVED)
    # def delegate_to_specialist(task: DelegateTaskInput) -> str:
    #     """Delegates a specific task to the appropriate specialist agent based on its name."""
    #     agent_to_call = specialists.get(task.agent_name)
    #     if agent_to_call:
    #         print(f"--- Delegating to {task.agent_name} ---")
    #         try:
    #             # Use .run() to execute the agent and get a response object
    #             response = agent_to_call.run(task.task_description)
    #             print(f"--- Response from {task.agent_name} received --- ")
    #             # Ensure response object is not None before accessing content
    #             response_content = response.content if response and hasattr(response, 'content') else str(response)
    #             # Log the received content
    #             print(f"--- Content from {task.agent_name}: ---\\n{response_content}\\n---------------------------------")
    #             return response_content
    #         except Exception as e:
    #             # Provide more specific error in the response
    #             print(f"Error running {task.agent_name}: {e}")
    #             return f"Error: Could not get response from {task.agent_name}. Details: {str(e)}"
    #     else:
    #         return f"Error: Specialist agent '{task.agent_name}' not found."

    # Define instructions for the Team's coordinator role, instructing direct delegation by name
    team_instructions = dedent(f"""
        You are the overall coordinator for a team of specialist agents designed to help users think better by applying mental models.
        Your goal is to understand the user's request and provide a comprehensive and helpful response.

        Available specialist agents (address them by name in your response to delegate tasks):
        {chr(10).join([f'- {name}: {agent.role}' for name, agent in specialists.items()])}

        Workflow:
        1. Analyze the user's request.
        2. Determine if the expertise of one or more specialist agents is required.
        3. If delegation is needed, **address the specific specialist agent directly by name** in your internal reasoning or plan. For example: "Okay, I need to ask the `decision_risk_agent` about the potential downsides..." or "Delegate to `problem_solving_innovation_agent`: Can you brainstorm alternative solutions?".
        4. **Crucially, you MUST address the specialist agent by their exact name** (e.g., `decision_risk_agent`, `problem_solving_innovation_agent`) for the system to route the task correctly.
        5. Synthesize the information received from the specialist agents along with your own analysis to formulate a final, comprehensive response to the user.
        6. Present the final response clearly using markdown.
    """)

    agent_team = Team(
        members=all_members,
        # tools=[delegate_to_specialist], # REMOVED - No explicit delegation tool needed
        tools=[ReasoningTools(add_instructions=True)], # Start with no specific coordinator tools for now
        model=llm,
        mode="coordinate",
        instructions=team_instructions, # Use updated instructions
        success_criteria="The user receives a helpful, synthesized response, correctly delegating tasks to specialists by name if necessary.",
        add_datetime_to_instructions=True,
        show_tool_calls=True, # Show tool calls *from* agents (if any)
        markdown=True,
        enable_agentic_context=True, # Allow agents to see context
        show_members_responses=True, # Show specialist responses for debugging
    )
    return agent_team

if __name__ == "__main__":
    print("Cognitive Assistant Agent Team - Starting...")

    # Check for API key before creating team
    if not settings.OPENROUTER_API_KEY:
        print("Exiting due to missing OpenRouter API key.")
        exit(1)

    cognitive_team = create_agent_team()
    print("Agent team created.")

    # --- Example Interaction Loop ---
    print("\nEnter your query or problem description (or type 'quit' to exit).")
    while True:
        user_query = input("> ")
        if user_query.lower() == 'quit':
            break
        if not user_query:
            continue

        print("\n--- Thinking ---")
        # The CoordinatorAgent (within the team) handles the interaction
        # In 'coordinate' mode, the team routes the message to the coordinator first.
        cognitive_team.print_response(
            message=user_query,
            stream=True, # Stream the response for better UX
            stream_intermediate_steps=True,
            show_full_reasoning=True,
        )
        print("\n---------------")

    print("\nCognitive Assistant Agent Team - Finished.") 