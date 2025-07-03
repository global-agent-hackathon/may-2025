import logging
from textwrap import dedent
from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.models.aws import Claude
from agno.tools import Function, tool
from anthropic import BaseModel
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from agents.model import BedrockModel
from agents.tools.parse_ad_requirements import Advertisement
from database_storage import upsert_draft_campaign
from database_storage.database import DraftCampaignTypes

logger = logging.getLogger(__name__)


class AdCopy(BaseModel):
    ad_copy_1: str = Field(..., description="First ad copy text")
    ad_copy_2: str = Field(..., description="Second ad copy text")


def create_generate_and_store_ad_copy_tool(
    session: AsyncSession,
    conversation_id: str,
) -> Function:
    @tool(
        name="generate_and_store_ad_copy",
        description=dedent("""
            Generate two original, copyright-compliant ad copy texts for the provided advertisement requirements,
            and store them as a draft in the campaign details database.
            You may also provide additional requirements (e.g., tone, keywords, style) to further guide the ad copy generation.
            Returns the generated ad copies and storage confirmation.
        """),
        show_result=True,
    )
    async def generate_and_store_ad_copy(
        advertisement: Advertisement,
        additional_requirements: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate two ad copy texts and store them in the draft campaign details.

        Args:
            advertisement (Advertisement): The advertisement requirements, including product, platform, and audience details.
            additional_requirements (Optional[str]): Additional requirements to further guide the ad copy generation (e.g., tone, keywords, style). Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing success status, generated ad copies, draft ID, and whether the draft is new.
        """
        base_instructions = dedent("""
            Generate two distinct, creative, and copyright-compliant ad copy texts for the following advertisement requirements.
            Each ad copy should be original, engaging, and suitable for the specified platform and audience.
            Do not use any copyrighted or trademarked phrases unless they are provided in the requirements.
        """)
        if additional_requirements:
            instructions = (
                base_instructions
                + "\n\nAdditional requirements to consider:\n"
                + additional_requirements
            )
        else:
            instructions = base_instructions

        agent = Agent(
            model=Claude(id=BedrockModel.CLAUDE_3_7_SONNET.value),
            instructions=instructions,
            response_model=AdCopy,
            show_tool_calls=False,
            markdown=False,
            telemetry=False,
        )
        try:
            result = agent.run(str(advertisement.model_dump())).content
            if not isinstance(result, AdCopy):
                logger.error(f"Unexpected LLM response type: {type(result)}")
                return {
                    "success": False,
                    "message": "Unexpected response from ad copy generator.",
                }

            draft_id, is_new = await upsert_draft_campaign(
                session=session,
                type=DraftCampaignTypes.AD_COPY,
                data=result.model_dump(),
                conversation_id=conversation_id,
            )
            return {
                "success": True,
                "ad_copies": result.model_dump(),
                "draft_id": draft_id,
                "is_new": is_new,
            }
        except Exception as e:
            logger.error(f"Failed to generate/store ad copy: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to generate/store ad copy: {str(e)}",
            }

    return generate_and_store_ad_copy
