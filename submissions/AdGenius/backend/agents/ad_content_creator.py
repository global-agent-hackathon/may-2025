from textwrap import dedent

from agno.agent import Agent
from agno.models.aws import Claude
from agno.tools.replicate import ReplicateTools
from sqlalchemy.ext.asyncio import AsyncSession

from agents.model import BedrockModel
from agents.tools.ad_copy_generation import create_generate_and_store_ad_copy_tool

from .tools.ad_image import (
    create_store_generated_ad_image_tool,
    describe_generated_ad_image,
)


def create_ad_content_creator_agent(
    db_session: AsyncSession,
    conversation_id: str,
    debug_mode: bool = False,
) -> Agent:
    """
    Creates an agent for generating ad copy and (optionally) ad creative images.
    """
    agent = Agent(
        name="AdContentCreator",
        model=Claude(id=BedrockModel.CLAUDE_3_5_SONNET.value),
        session_id=conversation_id,
        add_datetime_to_instructions=True,
        tools=[
            create_generate_and_store_ad_copy_tool(
                session=db_session,
                conversation_id=conversation_id,
            ),
            ReplicateTools(model="black-forest-labs/flux-schnell"),
            describe_generated_ad_image,
            create_store_generated_ad_image_tool(
                session=db_session,
                conversation_id=conversation_id,
            ),
        ],
        description=dedent("""
An agent that generates original ad copy and, if requested, creates and describes ad images for your campaign.
All content is tailored to your requirements and delivered in a clear, marketing-friendly format.
"""),
        instructions=dedent("""
You are an expert ad content creator specializing in generating high-performing ad copy and creative ideas.

Follow this workflow when generating ad content:
1. First, use the 'generate_and_store_ad_copy' tool to generate ad copy templates and best practices for the specified product, platform, and audience.
2. After generating ad copy, ask the user if they would like to generate an ad image.
3. If the user requests an image:
   a. Use ReplicateTools (`generate_media`) to generate the image based on the campaign requirements.
   b. Call the 'store_generated_ad_image' tool to store the generated image in the campaign database.
   c. Call the 'describe_generated_ad_image' tool to generate a human-readable description of the image.
4. Return the results (ad copy, and if applicable, the image and its description) to the user in a clear, conversational, and marketing-friendly style.

Additional guidelines:
- Present multiple copy options (e.g., headlines, body text) tailored to the campaign's target audience and platform.
- Provide actionable tips for improving ad effectiveness and adapting content to different platforms.
- Offer creative direction and suggestions for visuals, even if image generation is not available.
- Do NOT return raw JSON or structured data; focus on user-friendly, ready-to-use content.
- If any required campaign information is missing, politely ask the user for clarification before proceeding.
- You MUST pay close attention to copyright and intellectual property issues when generating content. Do not include or suggest any content (text, images, slogans, etc.) that may infringe on third-party copyrights or trademarks. Always ensure that generated content is original or properly attributed, and encourage the user to verify copyright compliance before using any generated material.
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


# uv run -m agents.ad_content_creator
if __name__ == "__main__":

    async def main():
        from database_storage.database import get_session

        async for db_session in get_session():
            agent = create_ad_content_creator_agent(
                db_session=db_session,
                conversation_id="test-session-002",
                debug_mode=True,
            )
            # prompt = """genenrate an image: A split screen vertical image (9:16 ratio). On the left side: a young Asian professional looking distracted during an office meeting in a
            #      modern conference room, checking their phone under the table with a worried expression. On the right side: a lonely golden retriever sitting patiently next to an
            #      untouched full dog food bowl in a modern apartment. The scene should convey emotional connection and worry. Style: clean, realistic, modern Chinese office and home
            #      setting."""
            prompt = "describe image https://replicate.delivery/xezq/6QOQRHqev62GMqFjN4balZgpychlg8bsn0mowe1E2RpyLeapA/out-0.webp"
            await agent.aprint_response(prompt, stream=True)
            if agent.images:
                for image in agent.images:
                    print(f"Image URL: {image.url}")

    import asyncio

    asyncio.run(main())
