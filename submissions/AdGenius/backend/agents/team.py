from pathlib import Path
from textwrap import dedent

from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.aws import Claude
from agno.storage.sqlite import SqliteStorage
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
from sqlalchemy.ext.asyncio import AsyncSession

from agents.ad_content_creator import create_ad_content_creator_agent
from agents.ad_researcher import create_ad_researcher_agent
from agents.campaign_publisher import create_campaign_publisher_agent
from agents.campaign_requirements_analyzer import (
    create_campaign_requirements_analyzer_agent,
)
from agents.constants import (
    AGENT_DB_NAME,
    AGENT_TABLE_NAME,
    MEMORY_DB_NAME,
    MEMORY_TABLE_NAME,
    STORAGE_DIR_NAME,
)
from agents.model import BedrockModel

# Ensure storage directory exists
STORAGE_DIR = Path(__file__).parent.parent / STORAGE_DIR_NAME
STORAGE_DIR.mkdir(exist_ok=True, parents=True)
AGENT_DB_FILE = STORAGE_DIR / AGENT_DB_NAME
MEMORY_DB_FILE = STORAGE_DIR / MEMORY_DB_NAME


# response both structured output and markdown text
# show the memors calls
# add reasoning
def create_agentic_team(
    db_session: AsyncSession,
    user_id: str,
    conversation_id: str,
    debug_mode: bool = False,
) -> Team:
    agent_storage = SqliteStorage(
        table_name=AGENT_TABLE_NAME, db_file=str(AGENT_DB_FILE)
    )
    memory_db = SqliteMemoryDb(
        table_name=MEMORY_TABLE_NAME,
        db_file=str(MEMORY_DB_FILE),
    )

    team = Team(
        name="AdGenius",
        mode="coordinate",
        model=Claude(
            id=BedrockModel.CLAUDE_3_7_SONNET.value,
        ),
        tools=[
            ReasoningTools(add_instructions=True, add_few_shot=True),
        ],
        members=[
            create_campaign_requirements_analyzer_agent(
                db_session=db_session,
                conversation_id=conversation_id,
                debug_mode=debug_mode,
            ),
            create_ad_researcher_agent(debug_mode=debug_mode),
            create_ad_content_creator_agent(
                db_session=db_session,
                conversation_id=conversation_id,
                debug_mode=debug_mode,
            ),
            create_campaign_publisher_agent(
                db_session=db_session,
                conversation_id=conversation_id,
                debug_mode=debug_mode,
            ),
        ],
        description=dedent("""
AdGenius Team is a coordinated group of AI experts for creating, researching, and optimizing ad campaigns.
The team analyzes requirements, researches trends, and provides actionable, data-driven insights and creative suggestions tailored to each platform.
"""),
        instructions=dedent("""
You are AdGenius Team, a group of AI assistants that help create and optimize ad campaigns.
Be helpful, concise, and friendly when assisting users.
Follow this specific workflow when handling ad campaign requests:
1. First, use CampaignRequirementsAnalyzer to parse the user's campaign requirements
2. If any requirements are missing or unclear, guide the user through providing the missing information step by step
3. Once all requirements are complete, present them to the user for review and ask for explicit confirmation
4. After user confirmation, ensure CampaignRequirementsAnalyzer stores them in the database
5. After requirements are stored, use AdResearcher to conduct research and generate a comprehensive campaign report
6. Next, use AdContentCreator to guide the user in creating ad content (text or image) tailored to the campaign requirements and research insights. Help the user generate, refine, and select ad copy and creative ideas, and provide actionable suggestions for both text and images.
7. Only trigger the CampaignPublisher agent if the user explicitly requests to publish or launch the campaign. Do not proceed to publishing automatically.
All ads will only be placed on the AdPublisher platform. Do not suggest or reference any other advertising platforms.
Provide specific, actionable advice and data-driven insights for advertising campaigns.
For creative suggestions, be specific and tailored to AdPublisher.
Always respect user privacy and data protection guidelines.
Use the reasoning tool when appropriate to show your thought process to the user.
When recommending ad strategies, use the specialized tools provided to give accurate information.
Present your findings in a clear, structured, and actionable format.
Maintain context across the entire workflow to ensure consistency in your recommendations.
"""),
        user_id=user_id,
        session_id=conversation_id,
        add_datetime_to_instructions=True,
        add_member_tools_to_system_message=True,
        enable_agentic_context=True,  # Allow the agent to maintain a shared context and send that to members.
        share_member_interactions=True,  # Share all member responses with subsequent member requests.
        show_members_responses=True,
        enable_team_history=True,
        num_of_interactions_from_history=5,
        enable_session_summaries=True,
        enable_user_memories=True,  # manage user memories
        show_tool_calls=True,
        markdown=True,
        storage=agent_storage,
        memory=Memory(db=memory_db),
        debug_mode=debug_mode,
        monitoring=True,
        telemetry=False,
    )
    return team


# uv run -m agents.team
if __name__ == "__main__":

    async def main():
        from database_storage.database import get_session

        async for db_session in get_session():
            assist = create_agentic_team(
                db_session, "user_team_123321", "conv_team_456654"
            )
            await assist.aprint_response(
                "Please call the testing tool",
                stream=True,
            )

    import asyncio

    asyncio.run(main())
