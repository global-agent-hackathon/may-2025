# Cognitive Assistant Agent Team

## Vision

An AI system composed of specialized agents that proactively observe user input (text, problems, documents), identify opportunities to apply relevant mental models, and offer insights, questions, or alternative framings to enhance the user's thinking, analysis, and decision-making, without requiring explicit model requests.

## Core Concept: The Agent Team

Instead of one monolithic agent trying to juggle many models, we design a team where different agents specialize in clusters of related models. This allows for deeper expertise within each agent and a more manageable architecture.

## Project Structure

```plaintext
.env                   # Optional: Store your OPENROUTER_API_KEY here
agents/
├── agents/            # Core agent implementations
│   ├── __init__.py
│   ├── coordinator.py # The coordinating agent
│   ├── specialist.py  # Base class for specialists
│   ├── decision_risk.py
│   ├── problem_solving.py
│   ├── systems_complexity.py
│   ├── bias_psychology.py
│   ├── strategy_competition.py
│   ├── learning_communication.py
│   └── efficiency_process.py
├── config/
│   ├── __init__.py
│   └── settings.py    # Handles configuration (API keys, model IDs)
├── tests/
│   └── test_team.py   # Basic tests for the team
├── __init__.py        # Makes 'agents' a package
├── main.py            # Main entry point to run the agent team
├── requirements.txt   # Project dependencies
├── implementation-plan.mdc # (Potentially outdated) Development plan
└── README.md          # This file
```

## Usage

### Setup

1.  **Clone the repository (if applicable).**

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment (using conda or venv)
    # conda create -n cognitive-agents python=3.11 -y
    python -m venv .venv

    # Activate the environment
    # conda activate cognitive-agents
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    Navigate to the project root directory (containing the `agents` folder) and run:
    ```bash
    pip install -r agents/requirements.txt
    ```
    Core dependencies:
    *   `agno`: The agent framework.
    *   `openai`: Used by `agno` for the chat model interface.
    *   `python-dotenv`: To load environment variables from a `.env` file.
    *   `pytest`: For running tests.

4.  **Configure API Key:**
    This application uses [OpenRouter](https://openrouter.ai/) to access various LLMs.
    *   **Method 1: Environment Variable:** Set the `OPENROUTER_API_KEY` environment variable:
        ```bash
        export OPENROUTER_API_KEY='your_openrouter_api_key_here'
        ```
    *   **Method 2: `.env` file:** Create a file named `.env` in the *project root directory* with the following content:
        ```dotenv
        OPENROUTER_API_KEY='your_openrouter_api_key_here'
        ```
    The application (via `config/settings.py`) will automatically load the key.

### Running the Application

From the project root directory, execute the main script:

```bash
python agents/main.py
```

This starts the interactive command-line interface. Enter your query or problem description at the `>` prompt. Type `quit` to exit.

### Running Tests

From the project root directory, run:

```bash
pytest agents/tests
```

Note: Tests requiring the OpenRouter API key will be skipped if the key is not configured.

## Architecture & Workflow

### Agents

1.  **Coordinator Agent (`coordinator.py`):**
    *   Acts as the main interface and orchestrator.
    *   Analyzes user input and determines if delegation is needed.
    *   Uses the `delegate_to_specialist` tool to call specialists.
    *   Synthesizes specialist responses with its own analysis for the final output.

2.  **Specialist Agents (`decision_risk.py`, etc.):**
    *   Inherit from `agents/agents/specialist.py`.
    *   Each focuses on a specific cluster of mental models.
    *   Invoked by the Coordinator via the `delegate_to_specialist` tool.
    *   **Implemented Specializations:**
        *   `decision_risk_agent`: Decision-making, risk assessment.
        *   `problem_solving_innovation_agent`: Problem-solving, creativity.
        *   `systems_complexity_agent`: Systems thinking, complex interactions.
        *   `bias_psychology_agent`: Cognitive biases, psychology.
        *   `strategy_competition_agent`: Strategy, market analysis.
        *   `learning_communication_agent`: Learning, communication.
        *   `efficiency_process_agent`: Process improvement, habits.

### Workflow (`coordinate` mode with explicit tool)

The system uses `agno.team.Team` configured in `coordinate` mode (`main.py`).

1.  **User Input:** Provided via the command line.
2.  **Team Invocation:** Input sent to `cognitive_team.print_response()`.
3.  **Coordinator Activation:** The `Team` routes the input to the `coordinator_agent` (the only direct member).
4.  **Coordinator Orchestration (LLM-Driven):** The `coordinator_agent`'s LLM, guided by its instructions, analyzes the input.
5.  **Tool Call (Delegation):** If specialist expertise is needed, the Coordinator LLM calls the `delegate_to_specialist` tool, specifying the target `agent_name` and `task_description`.
6.  **Specialist Execution:** The `delegate_to_specialist` function (defined in `main.py`) finds the relevant specialist agent instance and calls its `.run()` method with the task description.
7.  **Tool Response:** The specialist's response content is returned to the Coordinator LLM.
8.  **Response Synthesis:** The Coordinator LLM synthesizes the information from tool calls and its own analysis.
9.  **User Output:** The final response is streamed to the console.

### Triggering / Proactive Assistance

Proactive triggering (where the system offers insights without a direct request) is primarily handled by the `CoordinatorAgent`'s LLM based on its instructions and semantic understanding of the ongoing conversation or input. It looks for cues suggesting a mental model might be beneficial, such as keywords, problem structures, ambiguity, potential biases, goal mismatches, or contextual relevance.

### Interaction Design

The goal is for the interaction to be:
*   **Suggestive:** Offering perspectives, not dictating answers.
*   **Transparent:** Briefly mentioning relevant models or specialist contributions.
*   **Concise:** Providing clear insights, with options to elaborate.
*   **Controllable:** Allowing the user to guide the conversation (future enhancements could include configuration).

## Implementation Notes

*   **LLM Foundation:** Uses `agno.models.openrouter.OpenRouter`, configured via `config/settings.py`. Requires an `OPENROUTER_API_KEY`.
*   **Agent Framework:** Uses `agno` (`Agent`, `Team`).
*   **Model Knowledge:** Primarily embedded via prompt engineering in specialist agent instructions.
*   **Orchestration Logic:** Handled by the `CoordinatorAgent`'s LLM using the explicit `delegate_to_specialist` tool within the `agno.team.Team` framework (`coordinate` mode).

## Challenges

*   **Trigger Accuracy:** Making proactive suggestions relevant and timely.
*   **Context Window Limits:** Managing extensive context.
*   **Computational Cost:** Latency and cost of multiple LLM calls.
*   **Synthesis Quality:** Effectively integrating diverse insights.
*   **Over-reliance:** Ensuring the tool augments, rather than replaces, user thinking.

This approach transforms mental models from static concepts into dynamic tools wielded by specialized AI agents, creating a powerful cognitive assistant team to augment human thinking proactively.

## Example Queries

Here are some examples of queries you could provide to the agent team via the command line (`python agents/main.py`). These are designed to potentially engage different specialist agents:

*   **Triggering Decision & Risk / Strategy:**
    ```
    > Our SaaS product, 'AlphaMetric', has seen declining user engagement over the past two quarters despite significant marketing spend ($150k). Development costs are ongoing. A new competitor just launched a similar tool with a freemium model. Should we double down on AlphaMetric with a major feature overhaul, pivot resources to develop a new, simpler tool 'BetaSimple' based on recent user feedback (estimated 3-month build), or initiate a strategic partnership exploration?
    ```
    *(Look for discussion of Sunk Cost, Opportunity Cost, Decision Trees, SWOT, Competitive Analysis)*

*   **Triggering Problem Solving / Innovation / Strategy:**
    ```
    > We run a local bookstore, and foot traffic is consistently down 20% year-over-year due to online retailers. Our current marketing (local flyers, occasional social media posts) isn't working. We need fundamentally new ideas to attract customers and create a unique value proposition beyond just selling books. How should we approach brainstorming this?
    ```
    *(Look for suggestions like First Principles, Reverse Thinking, Lateral Thinking, SWOT, Blue Ocean Strategy)*

*   **Triggering Systems & Complexity / Efficiency & Process:**
    ```
    > Our software development cycle involves QA finding bugs late in the process, which causes delays as developers switch context back from new features. This pushes release dates, frustrating the product team and sales who have made commitments. Improving QA resources helped slightly but didn't solve the core issue. How can we analyze this workflow to find better leverage points?
    ```
    *(Look for discussion of Feedback Loops, Bottlenecks, Systems Thinking, PDCA Cycle)*

*   **Triggering Bias & Psychology / Learning & Communication:**
    ```
    > I presented my proposal for streamlining our onboarding process, backed by data showing potential time savings. However, the department head dismissed it quickly, saying 'This isn't how we've done things, and the current system works fine for most people.' I feel strongly my data is solid. How might cognitive biases be playing a role here, and how can I re-approach this communication more effectively?
    ```
    *(Look for discussion of Confirmation Bias, Status Quo Bias, Loss Aversion, Framing, Pyramid Principle)*

*   **Triggering Efficiency & Process / Learning:**
    ```
    > I want to learn data analysis using Python in my spare time, but I keep getting distracted or losing motivation after a week or two. I have the resources (courses, books) but struggle with consistency. How can I apply behavioral models to build a sustainable learning habit?
    ```
    *(Look for discussion of Fogg Behavior Model, Hook Model, Chunking, Metacognition)*

Remember, the coordinator agent synthesizes the final response, potentially incorporating insights implicitly or explicitly from specialists invoked via the `delegate_to_specialist` tool.
