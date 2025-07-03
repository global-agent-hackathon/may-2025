import logging
from typing import Any, Dict, List

from agno.agent import Agent
from agno.models.aws import Claude
from agno.tools import tool
from agno.tools.function import Function
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from agents.model import BedrockModel
from database_storage import upsert_draft_campaign
from database_storage.database import DraftCampaignTypes

# Configure logging
logger = logging.getLogger(__name__)


class Advertisement(BaseModel):
    product_or_service: str = Field(
        ..., description="Product or service being advertised"
    )
    product_or_service_url: str = Field(
        ..., description="URL of the product or service"
    )
    campaign_name: str = Field(..., description="Name of the ad campaign")
    target_audience: str = Field(
        ..., description="Target audience for the advertisement"
    )
    geography: str = Field(..., description="Geographic region for ad targeting")
    ad_format: str = Field(
        ..., description="Format of the ad (e.g., video, image, carousel)"
    )
    budget: str = Field(..., description="Budget for the campaign (e.g., $5000)")
    platform: str = Field(
        ..., description="The platform for ad placement (e.g., TikTok, Facebook)"
    )
    kpi: str = Field(
        ...,
        description="Key performance indicator (e.g., installs, registrations, conversion rate, etc.)",
    )
    time_period: str = Field(
        default="",
        description="Time period for the ad campaign (e.g., 2024-06-01 to 2024-06-30)",
    )
    creative_direction: str = Field(
        default="",
        description="Specific creative requirements or direction for the ad (if any)",
    )
    other_details: List[str] = Field(
        default=[],
        description="Other relevant details about the advertising requirement",
    )


REQUIRED_FIELDS = [
    "product_or_service",
    "product_or_service_url",
    "campaign_name",
    "target_audience",
    "geography",
    "ad_format",
    "budget",
    "platform",
    "kpi",
]


def _get_missing_fields(ad: Advertisement) -> List[str]:
    missing = []
    for field in REQUIRED_FIELDS:
        value = getattr(ad, field, None)
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing


@tool(
    name="parse_advertisement_requirements",
    description="Parse ad requirements and return structured Advertisement. If info is missing, ask user for more.",
    show_result=True,
)
def parse_advertisement_requirements(input: str) -> Dict[str, Any]:
    """
    Parse advertisement requirements and return structured Advertisement.

    Args:
        input: User input containing advertisement requirements.

    Returns:
        A dictionary containing the parsed advertisement details or a message indicating missing information.
    """

    agent = Agent(
        model=Claude(id=BedrockModel.CLAUDE_3_5_HAIKU.value),
        instructions=[
            "Extract the following fields from the user's input and return them as a JSON object:",
            "- product_or_service",
            "- product_or_service_url",
            "- campaign_name",
            "- target_audience",
            "- geography",
            "- ad_format",
            "- budget",
            "- platform",
            "- kpi",
            "- time_period",
            "- creative_direction",
            "- other_details",
            "If any required field is missing or unclear, leave it blank.",
        ],
        response_model=Advertisement,
        show_tool_calls=False,
        markdown=False,
        telemetry=False,
    )
    result = agent.run(input).content

    if isinstance(result, Advertisement):
        missing = _get_missing_fields(result)
        if missing:
            return {
                "success": False,
                "message": f"Please provide the following missing information: {', '.join(missing)}",
                "missing_fields": missing,
                "partial_advertisement": result.model_dump_json(),
            }
        else:
            return {
                "success": True,
                "advertisement": result.model_dump_json(),
            }
    else:
        return {
            "success": False,
            "message": "Could not parse the advertisement requirements. Please provide more details.",
            "missing_fields": REQUIRED_FIELDS,
        }


def create_store_advertisement_requirements_tool(
    session: AsyncSession,
    conversation_id: str,
) -> Function:
    """
    Create a tool to store advertisement requirements in the database.
    """

    @tool(
        name="store_advertisement_requirements",
        description="Store advertisement requirements in the database as a draft campaign.",
        show_result=True,
    )
    async def store_advertisement_requirements(
        advertisement: Advertisement,
    ) -> Dict[str, Any]:
        """
        Store advertisement requirements in the database as a draft campaign.

        Args:
            advertisement: Parsed advertisement requirements

        Returns:
            A dictionary containing the result of the storage operation
        """

        logger.info(f"Storing advertisement requirements: {advertisement!r}")

        try:
            missing_fields = _get_missing_fields(advertisement)
            if missing_fields:
                return {
                    "success": False,
                    "message": f"Missing required fields: {', '.join(missing_fields)}",
                    "missing_fields": missing_fields,
                }

            # Store the requirements as a draft campaign (create or update if exists)
            draft_id, is_new = await upsert_draft_campaign(
                session=session,
                type=DraftCampaignTypes.REQUIREMENTS,
                data=advertisement.model_dump(),
                conversation_id=conversation_id,
            )

            action = "created" if is_new else "updated"
            logger.info(
                f"Successfully {action} advertisement requirements with draft_id: {draft_id}"
            )
            return {
                "success": True,
                "message": f"Advertisement requirements {action} successfully",
                "draft_id": draft_id,
                "is_new": is_new,
            }
        except Exception as e:
            logger.error(
                f"Failed to store advertisement requirements: {str(e)}", exc_info=True
            )
            return {
                "success": False,
                "message": f"Failed to store advertisement requirements: {str(e)}",
            }

    return store_advertisement_requirements
