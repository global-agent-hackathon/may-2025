from textwrap import dedent

from agno.agent import Agent
from agno.models.aws import Claude
from sqlalchemy.ext.asyncio import AsyncSession

from agents.model import BedrockModel

from .tools.parse_ad_requirements import (
    create_store_advertisement_requirements_tool,
    parse_advertisement_requirements,
)


def create_campaign_requirements_analyzer_agent(
    db_session: AsyncSession,
    conversation_id: str,
    debug_mode: bool = False,
) -> Agent:
    agent = Agent(
        name="CampaignRequirementsAnalyzer",
        model=Claude(id=BedrockModel.CLAUDE_3_7_SONNET.value),
        session_id=conversation_id,
        add_datetime_to_instructions=True,
        tools=[
            parse_advertisement_requirements,
            create_store_advertisement_requirements_tool(
                conversation_id=conversation_id, session=db_session
            ),
        ],
        description=dedent("""
An agent that analyzes advertising requirements, identifies missing or unclear information, and helps the user complete a comprehensive campaign brief.
"""),
        instructions=dedent("""
You are an expert at analyzing advertising requirements.
Follow this step-by-step workflow when handling ad campaign requirements:
1. Use the 'parse_advertisement_requirements' tool to extract structured data and check for missing information.
2. If the tool output indicates missing or unclear fields (success: False):
   - Clearly list each missing field one by one
   - Ask the user about ONLY ONE missing field at a time in a friendly, conversational way
   - Wait for the user's response before asking about the next missing field
   - After each user response, run the parse tool again to check if all requirements are complete
3. For each field, provide helpful examples and context to guide the user
4. Once ALL requirements are complete (success: True), present a clear summary of all requirements to the user
5. Explicitly ask the user to confirm if they want to proceed with storing these requirements
6. Only after receiving explicit confirmation, use the 'store_advertisement_requirements' tool to save them to the database
7. After storing, confirm that the requirements have been saved successfully
8. Let the user know that the AdResearcher will now generate a campaign report based on these requirements
- Offer suggestions to improve clarity or effectiveness of the requirements.
- Do NOT return structured data or JSON; focus on clear, conversational feedback.
"""),
        add_name_to_instructions=True,
        markdown=True,
        show_tool_calls=True,
        debug_mode=debug_mode,
        telemetry=False,
        monitoring=True,
        enable_user_memories=False,
        enable_agentic_memory=False,
    )
    return agent


# uv run -m agents.campaign_requirements_analyzer
if __name__ == "__main__":

    async def main():
        from database_storage.database import get_session

        async for db_session in get_session():
            agent = create_campaign_requirements_analyzer_agent(
                db_session=db_session, conversation_id="123223", debug_mode=True
            )
            ad_requirement = """
                please store the requirements:
                 product_or_service_url: https://app.doyogawithme.com/download
                 campaign_name: YogaBliss SEA Launch
                 target_audience: Southeast Asian women ages 25-45
                 geography: Singapore, Malaysia, Philippines
                 ad_format: Standard display banners
                 budget: $5000
                 platform: Facebook, Instagram
                 kpi: CPI'
            """
            await agent.aprint_response(ad_requirement, stream=True)

    import asyncio

    asyncio.run(main())
