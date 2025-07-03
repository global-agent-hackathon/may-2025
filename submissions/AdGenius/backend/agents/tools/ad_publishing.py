import logging
from textwrap import dedent
from typing import Any, Dict, List

from agno.agent import Agent
from agno.models.aws import Claude
from agno.tools import Function, tool
from anthropic import BaseModel
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from ad_publisher.service import AdPublisherError, publish_campaign_and_ad
from agents.model import BedrockModel
from database_storage import get_conversation_draft_campaigns, upsert_draft_campaign
from database_storage.database import DraftCampaignTypes

# Configure logging
logger = logging.getLogger(__name__)


class CampaignDetails(BaseModel):
    campaign_name: str = Field(..., description="Name of the campaign")
    product_name: str = Field(..., description="Name of the product or service")
    product_url: str = Field(..., description="URL for the product or service")
    start_date: str = Field(
        ..., description="Campaign start date in ISO format (YYYY-MM-DD)"
    )
    campaign_description: str = Field(..., description="Description of the campaign")
    campaign_end_date: str = Field(
        ..., description="Campaign end date in ISO format (YYYY-MM-DD)"
    )
    campaign_status: str = Field("active", description="Status for the campaign")
    campaign_budget: float = Field(..., description="Budget as a float number")
    campaign_image_url: str = Field(..., description="Image URL for the campaign")
    ad_title: str = Field(..., description="Title for the advertisement")
    ad_target_url: str = Field(..., description="Target URL for the ad")
    ad_description: str = Field(..., description="Description for the advertisement")
    ad_image_url: str = Field(..., description="Image URL for the advertisement")
    ad_status: str = Field("active", description="Status for the ad")


def get_campaign_details_from_draft(
    draft_campaigns: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Use an agent to parse the campaign and ad details from draft campaigns.

    Args:
        draft_campaigns: List of draft campaign dictionaries

    Returns:
        Dict containing all the parameters needed for publish_campaign_and_ad
    """
    instructions = """
    Given the following draft campaign details, extract the information needed to publish an ad campaign.
    Some fields may not be present in the data. Use any field in any draft campaign that seems relevant.
    Make reasonable assumptions when data is missing or needs formatting.

    For numeric values like campaign_budget, ensure they are converted to the appropriate format (e.g., float).
    If ad_target_url is not specified, use product_url.
    """

    agent = Agent(
        model=Claude(id=BedrockModel.CLAUDE_3_5_SONNET.value),
        instructions=instructions,
        response_model=CampaignDetails,
        add_datetime_to_instructions=True,
        show_tool_calls=False,
        markdown=False,
        telemetry=False,
    )

    try:
        result = agent.run(str(draft_campaigns)).content
        if not isinstance(result, CampaignDetails):
            logger.error(f"Unexpected LLM response type: {type(result)}")
            return {}

        # Convert to dict and handle any post-processing
        campaign_details = result.model_dump()

        # Ensure campaign_budget is a float if present as string
        if isinstance(campaign_details.get("campaign_budget"), str):
            budget_str = (
                campaign_details["campaign_budget"].replace("$", "").replace(",", "")
            )
            try:
                campaign_details["campaign_budget"] = float(budget_str)
            except ValueError:
                campaign_details["campaign_budget"] = None

        # Ensure ad_target_url is set (default to product_url if not present)
        if not campaign_details.get("ad_target_url") and campaign_details.get(
            "product_url"
        ):
            campaign_details["ad_target_url"] = campaign_details.get("product_url")

        return campaign_details
    except Exception as e:
        logging.error(f"Error parsing agent response: {str(e)}")
        return {}


def create_publish_ad_to_platform_tool(
    session: AsyncSession, conversation_id: str
) -> Function:
    @tool(
        name="publish_ad_to_platform",
        description=dedent(
            """
            Publishes the prepared ad (copy, image, and metadata) to the specified ad platform.
            Requires all necessary campaign and creative information.
            """
        ),
        show_result=True,
    )
    async def publish_ad_to_platform() -> Dict[str, Any]:
        """
        Publishes the ad to the specified platform.
        Returns:
            dict: Result of the publishing attempt (success, message, platform_response).
        """
        try:
            # Load all draft campaigns for this conversation
            draft_campaigns = await get_conversation_draft_campaigns(
                session=session, conversation_id=conversation_id
            )

            if not draft_campaigns:
                return {
                    "success": False,
                    "message": "No draft campaigns found for this conversation.",
                }

            # Use Agno agent to parse the campaign details from draft campaigns
            campaign_details = get_campaign_details_from_draft(draft_campaigns)

            if not campaign_details:
                return {
                    "success": False,
                    "message": "Failed to parse campaign details from draft campaigns.",
                }

            # Extract required fields
            campaign_name = campaign_details.get("campaign_name")
            product_name = campaign_details.get("product_name")
            product_url = campaign_details.get("product_url")
            start_date = campaign_details.get("start_date")

            # Check if we have the minimum required fields
            if not all([campaign_name, product_name, product_url]):
                missing_fields = []
                if not campaign_name:
                    missing_fields.append("campaign_name")
                if not product_name:
                    missing_fields.append("product_name")
                if not product_url:
                    missing_fields.append("product_url")

                return {
                    "success": False,
                    "message": f"Missing required fields for campaign: {', '.join(missing_fields)}",
                }

            # Extract other fields from the parsed data
            campaign_description = campaign_details.get("campaign_description")
            campaign_end_date = campaign_details.get("campaign_end_date")
            campaign_status = campaign_details.get("campaign_status", "active")
            
            # Ensure budget is a float
            campaign_budget = None
            if campaign_details.get("campaign_budget") is not None:
                try:
                    # First convert to string to handle any object type, then to float
                    budget_str = str(campaign_details.get("campaign_budget")).replace("$", "").replace(",", "").strip()
                    campaign_budget = float(budget_str)
                except (ValueError, TypeError):
                    logger.warning("Invalid campaign budget value, setting to None")
            
            campaign_image_url = campaign_details.get("campaign_image_url")

            # Ad details
            ad_title = campaign_details.get("ad_title")
            ad_description = campaign_details.get("ad_description")
            ad_target_url = campaign_details.get("ad_target_url", product_url)
            ad_image_url = campaign_details.get("ad_image_url")
            ad_status = campaign_details.get("ad_status", "active")

            # Now call the ad platform API to publish
            campaign_id, campaign_success, ad_data = await publish_campaign_and_ad(
                session=session,
                conversation_id=conversation_id,
                campaign_name=str(campaign_name),
                product_name=str(product_name),
                product_url=str(product_url),
                start_date=str(start_date),
                campaign_description=campaign_description,
                campaign_end_date=campaign_end_date,
                campaign_status=campaign_status,
                campaign_budget=campaign_budget,
                campaign_image_url=campaign_image_url,
                ad_title=ad_title,
                ad_target_url=ad_target_url,
                ad_description=ad_description,
                ad_image_url=ad_image_url,
                ad_status=ad_status,
            )

            if not campaign_success:
                return {
                    "success": False,
                    "message": "Failed to publish campaign to the platform.",
                    "campaign_id": campaign_id,
                }

            # If no ad data but campaign was successful
            if not ad_data:
                # Create a record of the successful campaign publication
                publication_data = {
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_name,
                    "product_name": product_name,
                    "status": "published",
                    "campaign_only": True,
                    "publication_date": start_date,
                    "publisher_id": campaign_id,  # Include publisher ID from response
                }

                draft_id, is_new = await upsert_draft_campaign(
                    session=session,
                    type=DraftCampaignTypes.PUBLISHED_CAMPAIGN,
                    data=publication_data,
                    conversation_id=conversation_id,
                )

                return {
                    "success": True,
                    "message": "Campaign published successfully, but no ad was created.",
                    "campaign_id": campaign_id,
                    "draft_id": draft_id,
                    "platform_response": {
                        "status": "active",
                        "campaign_only": True,
                    },
                }

            # Both campaign and ad were published
            # Create a record of the successful campaign and ad publication
            publication_data = {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "product_name": product_name,
                "ad_id": ad_data.get("id") or "unknown",
                "ad_title": ad_title,
                "ad_status": ad_data.get("status") or "active",
                "ad_url": ad_data.get("targetUrl", ad_target_url) or "",
                "status": "published",
                "publication_date": start_date,
                "publisher_id": campaign_id,  # Include publisher ID from response
                "ad_metrics": ad_data.get("metrics", {}),  # Include metrics if available
            }

            draft_id, is_new = await upsert_draft_campaign(
                session=session,
                type=DraftCampaignTypes.PUBLISHED_CAMPAIGN,
                data=publication_data,
                conversation_id=conversation_id,
            )

            return {
                "success": True,
                "message": "Ad published successfully.",
                "campaign_id": campaign_id,
                "draft_id": draft_id,
                "platform_response": {
                    "ad_id": ad_data.get("id") or "unknown",
                    "status": ad_data.get("status") or "active",
                    "platform_url": ad_data.get("targetUrl", ad_target_url) or "",
                    "metrics": ad_data.get("metrics", {}),
                    "created_at": ad_data.get("createdAt", ""),
                    "updated_at": ad_data.get("updatedAt", ""),
                },
            }

        except AdPublisherError as e:
            logger.error(f"Ad Publisher error: {str(e)}")
            return {
                "success": False,
                "message": f"Ad publishing error: {str(e)}",
            }
        except Exception as e:
            logger.exception(f"Unexpected error in publish_ad_to_platform: {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}",
            }

    return publish_ad_to_platform
