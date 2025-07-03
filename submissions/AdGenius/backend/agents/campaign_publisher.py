from textwrap import dedent

from agno.agent import Agent
from agno.models.aws import Claude
from sqlalchemy.ext.asyncio import AsyncSession

from agents.model import BedrockModel

from .tools.ad_publishing import create_publish_ad_to_platform_tool


def create_campaign_publisher_agent(
    db_session: AsyncSession,
    conversation_id: str,
    debug_mode: bool = False,
) -> Agent:
    agent = Agent(
        name="CampaignPublisher",
        model=Claude(id=BedrockModel.CLAUDE_3_5_SONNET.value),
        session_id=conversation_id,
        add_datetime_to_instructions=True,
        tools=[
            create_publish_ad_to_platform_tool(
                session=db_session,
                conversation_id=conversation_id,
            ),
        ],
        description=dedent("""
An agent that publishes finalized ad campaigns to AdPublisher.
It handles the delivery of ad creative, copy, and metadata to the AdPublisher platform.
"""),
        instructions=dedent("""
You are an expert campaign publisher responsible for launching ad campaigns on AdPublisher, which is the only platform where ads will be published.

Important: Only proceed with publishing if the user explicitly requests to publish or launch the campaign. Do not initiate publishing automatically.

Workflow:
1. Wait for the user to explicitly request publishing or launching the campaign.
2. Once requested, ensure you have received the complete, user-approved campaign requirements and creative assets (ad copy, images, targeting, budget, etc.).
3. Use the 'publish_ad_to_platform' tool to publish the ad to AdPublisher (the only supported platform).
4. Confirm successful publication or report any errors encountered during the process.
5. If publication fails, provide a clear explanation and suggest next steps or troubleshooting.
6. After successful publishing, return a summary including:
   - Confirmation that the ad was published to AdPublisher
   - Links to the live ads (if available)
   - Any relevant platform responses or IDs

Guidelines:
- Ensure all required information is present before attempting to publish. If anything is missing, clearly state what is needed.
- Do NOT return raw JSON or structured data; always communicate in a clear, user-friendly, and actionable manner.
- Pay close attention to copyright and intellectual property issues. Do not publish or suggest content that may infringe on third-party rights.
- Encourage the user to verify the ad's appearance and compliance on AdPublisher after publishing.
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


# uv run -m agents.campaign_publisher
if __name__ == "__main__":

    async def main():
        from database_storage.database import get_session

        async for db_session in get_session():
            agent = create_campaign_publisher_agent(
                db_session=db_session,
                conversation_id="test-session-publish-001",
                debug_mode=True,
            )
            prompt = (
                "Publish this ad to AdPublisher: "
                "Headline: 'Try YogaBliss Today!' "
                "Body: 'Experience yoga at home with Southeast Asia's top instructors. Download now.' "
                "Image URL: https://example.com/yogabliss-ad.jpg "
                "Target: Women, 25-45, Singapore, Malaysia, Philippines "
                "Budget: $500 "
            )
            await agent.aprint_response(prompt, stream=True)

    import asyncio

    asyncio.run(main())
