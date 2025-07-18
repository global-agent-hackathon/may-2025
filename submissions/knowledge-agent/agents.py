from typing import List
from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.reasoning import ReasoningTools
from agno.team import Team
from pydantic import BaseModel

DEFAULT_MODEL_ID = "gpt-4o"
DEFAULT_BASE_URL = "https://api.openai.com/v1"

common_tools = [ReasoningTools(add_instructions=True)]


class Result(BaseModel):
    """Uniform payload returned by every agent"""
    result: str

class CoverageCSV(BaseModel):
    """The agent must return a single CSV string."""
    csv: str

class QuizItem(BaseModel):
    question: str
    options: List[str]
    correct_index: int

class Quiz(BaseModel):
    questions: List[QuizItem]

def create_analysis_team(api_key: str, base_url: str = DEFAULT_BASE_URL, model_id: str = DEFAULT_MODEL_ID):
    """Create a team of analysis agents"""

    # Create model
    model = OpenAILike(
        id=model_id,
        api_key=api_key,
        base_url=base_url
    )

    # Create specialized agents
    summarizer = Agent(
        name="Summarizer",
        role="Creates concise summaries of text content",
        model=model,
        instructions=["Focus on key points", "Be concise and clear"],
        markdown=True,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
    )

    analyzer = Agent(
        name="Analyzer",
        role="Provides detailed analysis of content",
        model=model,
        instructions=["Identify patterns and themes", "Provide insights and implications"],
        markdown=True,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
    )

    concept_mapper = Agent(
        name="Concept Mapper",
        role="Builds a concept graph",
        model=model,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
        expected_output="digraph {",
        instructions=[
            "Return ONLY GraphViz DOT that starts with `digraph {` and ends with `}`.",
            "Use lines like `A -> B;` for edges.",
            "Do NOT wrap the code in back-ticks. No explanations."
        ],
    )

    key_points_extractor = Agent(
        name="Key Points Extractor",
        role="Extracts bullet-point key information",
        model=model,
        instructions=["List the most important points", "Use clear bullet points"],
        markdown=True,
        response_model=Result,
        use_json_mode=True,
    )

    intersection_finder = Agent(
        name="Intersection Finder",
        role="Finds entities / claims mentioned by at least two sources",
        model=model,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
        instructions=[
            "Return a markdown table where rows are items and columns are Source 1, Source 2, ...",
            "DO NOT add backticks in the beginning of the table. Just the table.",
            "Mark a ✓ when the item appears in that source.",
            "Limit to the 15 most frequent items, ordered by number of sources.",
        ],
    )

    coverage_agent = Agent(
        name="Coverage Analyst",
        role="Builds a source-by-topic coverage matrix",
        model=model,
        tools=common_tools,
        response_model=CoverageCSV,
        use_json_mode=True,
        expected_output="\",Source 1",
        instructions=[
            "Step 1 Find up to 10 sub-topics that span the sources.",
            "Step 2 Create a CSV with header: Topic,Source 1,Source 2,…",
            "Put ✓ where the topic appears, leave blank otherwise.",
            "Return **exactly** the JSON object {\"csv\": \"<the CSV>\"}.",
            "NO markdown, NO back-ticks, NO commentary."
        ],
    )

    quiz_agent = Agent(
        name="Quiz Maker",
        role="Creates multiple-choice questions to reinforce learning",
        model=model,
        tools=common_tools,
        response_model=Quiz,
        use_json_mode=True,  # emits {"questions":[{...}, ...]}
        expected_output="\"questions\": [",  # quick structural check
        instructions=[
            "Write 5-10 items covering key facts across all sources.",
            "Each item has fields: question (str), options (list of 4), correct_index (int 0-3).",
            "Return ONLY the JSON object matching the schema—no markdown, no prose, no back-ticks."
        ],
    )

    # Create team
    team = Team(
        name="Analysis Team",
        mode="route",
        model=model,
        members=[summarizer, analyzer, concept_mapper, key_points_extractor, intersection_finder, coverage_agent, quiz_agent],
        instructions=[
            # explicit mapping so the router never guesses wrong
            "Always use this mapping:",
            "  📄 Summary            → Summarizer",
            "  🔍 In-depth Analysis  → Analyzer",
            "  🗺️ Concept Map        → Concept Mapper",
            "  🎯 Key Points         → Key Points Extractor",
            "  🔗 Intersections      → Intersection Finder",
            "  🧭 Topic Coverage     → Coverage Analyst",
            "  📝 Knowledge Check    → Quiz Maker",
            "Return the chosen member's response **verbatim**; never rewrite it.",
            "Ensure the output matches the requested length (Brief/Standard/Detailed)",
            "Do NOT add introductory or closing notes.",
        ],
        enable_agentic_context=True,
        debug_mode=False
    )

    return team
