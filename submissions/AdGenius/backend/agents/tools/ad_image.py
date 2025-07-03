from textwrap import dedent
from typing import Any, Dict

import httpx
from agno.agent import Agent
from agno.media import Image
from agno.models.aws import Claude
from agno.tools import Function, tool
from sqlalchemy.ext.asyncio import AsyncSession

from agents.model import BedrockModel
from database_storage import upsert_draft_campaign
from database_storage.database import DraftCampaignTypes


@tool(
    name="describe_generated_ad_image",
    description=dedent("""
        Analyze and generate a descriptive summary of the provided advertisement image.
        This tool uses an LLM to interpret the image and return a human-readable description,
        which can be used for accessibility, review, or campaign documentation purposes.
        Returns the generated description as a string.
    """),
    show_result=True,
)
async def describe_generated_ad_image(url: str) -> str:
    """
    Generate a descriptive summary of the provided advertisement image.

    Args:
        url (str): The URL of the image to be described.

    Returns:
        str: A human-readable description of the image content.
    """
    agent = Agent(
        model=Claude(id=BedrockModel.CLAUDE_3_7_SONNET.value),
        markdown=True,
        telemetry=False,
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        response.raise_for_status()
        image_bytes = response.content

    response = agent.run(
        "Tell me about this image", images=[Image(content=image_bytes)], stream=False
    )
    return str(response.content)


def create_store_generated_ad_image_tool(
    session: AsyncSession,
    conversation_id: str,
) -> Function:
    @tool(
        name="store_generated_ad_image",
        description=dedent("""
            Store the generated advertisement image URL as a draft in the campaign details database.
            This tool saves the image reference for later use or review, and returns storage confirmation
            along with the draft ID and whether the draft is newly created.
        """),
        show_result=True,
    )
    async def store_generated_ad_image(url: str) -> Dict[str, Any]:
        """
        Store the generated advertisement image URL as a draft in the campaign details database.

        Args:
            url (str): The URL of the generated advertisement image.

        Returns:
            Dict[str, Any]: A dictionary containing success status, image data, draft ID, and whether the draft is new.
        """
        data = {"url": url}
        draft_id, is_new = await upsert_draft_campaign(
            session=session,
            type=DraftCampaignTypes.AD_IMAGE,
            data={"url": url},
            conversation_id=conversation_id,
        )

        return {
            "success": True,
            "ad_image": data,
            "draft_id": draft_id,
            "is_new": is_new,
        }

    return store_generated_ad_image
