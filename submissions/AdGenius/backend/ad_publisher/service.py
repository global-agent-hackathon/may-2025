"""
Services for ad campaign and ad publishing

This module provides services for publishing campaigns and ads to the Ad Publisher API
and storing them in the database.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from ad_publisher.ad_publisher import (
    AdPublisherError,
)
from ad_publisher.ad_publisher import (
    create_ad as api_create_ad,
)
from ad_publisher.ad_publisher import (
    create_campaign as api_create_campaign,
)
from database_storage import (
    create_campaign as db_create_campaign,
)
from database_storage import (
    get_campaign,
    update_campaign_publisher_data,
)

# Configure logging
logger = logging.getLogger(__name__)


async def publish_campaign_and_ad(
    session: AsyncSession,
    conversation_id: str,
    campaign_name: str,
    product_name: str,
    product_url: str,
    start_date: str,
    campaign_description: Optional[str] = None,
    campaign_end_date: Optional[str] = None,
    campaign_status: Optional[str] = None,
    campaign_budget: Optional[float] = None,
    campaign_image_url: Optional[str] = None,
    ad_title: Optional[str] = None,
    ad_target_url: Optional[str] = None,
    ad_description: Optional[str] = None,
    ad_image_url: Optional[str] = None,
    ad_status: Optional[str] = None,
) -> Tuple[str, bool, Optional[Dict[str, Any]]]:
    """
    Create a campaign in the database, publish it to the Ad Publisher API,
    and optionally create and publish an ad for this campaign.

    Args:
        session: Database session
        conversation_id: Conversation ID associated with this campaign
        campaign_name: Name of the campaign
        product_name: Name of the product being advertised
        product_url: URL for the product
        start_date: Campaign start date (ISO format string)
        campaign_description: Optional campaign description
        campaign_end_date: Optional campaign end date (ISO format string)
        campaign_status: Optional campaign status for API
        campaign_budget: Optional campaign budget
        campaign_image_url: Optional image URL for the campaign
        ad_title: Optional title of the advertisement. If provided, an ad will be created.
        ad_target_url: Optional target URL for the advertisement. Required if ad_title is provided.
        ad_description: Optional advertisement description
        ad_image_url: Optional URL to the advertisement image
        ad_status: Optional advertisement status

    Returns:
        Tuple of (campaign_id, campaign_success_flag, ad_data_if_successful)
        ad_data_if_successful will be None if ad creation was not attempted or failed.

    Raises:
        Various exceptions from the database or API operations
    """
    # First, create a campaign in our database
    campaign_id = await db_create_campaign(
        session=session,
        conversation_id=conversation_id,
        campaign_name=campaign_name,
        product_name=product_name,
        product_url=product_url,
        start_date=start_date,
        description=campaign_description,
        end_date=campaign_end_date,
        status="pending",  # We'll update this after API call
        budget=str(campaign_budget) if campaign_budget is not None else None,
        image_url=campaign_image_url,
    )

    publisher_id: Optional[str] = None
    campaign_api_response: Optional[Dict[str, Any]] = None
    campaign_success = False
    ad_data: Optional[Dict[str, Any]] = None

    # Now try to publish the campaign to the API
    try:
        api_campaign_response = api_create_campaign(
            name=campaign_name,
            startDate=start_date,
            description=campaign_description,
            endDate=campaign_end_date,
            status=campaign_status,
            budget=campaign_budget,
        )

        # Extract campaign id from the nested response structure
        publisher_id = api_campaign_response.get("campaign", {}).get("id")
        if not publisher_id:
            logger.error(f"API response missing campaign ID: {api_campaign_response}")
            await update_campaign(
                session,
                campaign_id,
                status="error",
                error_message="API response missing campaign ID",
            )
            return campaign_id, False, None

        campaign_api_response = api_campaign_response
        await update_campaign_publisher_data(
            session, campaign_id, publisher_id, campaign_api_response
        )
        await update_campaign(session, campaign_id, status="active")
        campaign_success = True

    except AdPublisherError as e:
        error_message = str(e)
        logger.error(f"Error creating campaign in API: {error_message}")
        await update_campaign(
            session,
            campaign_id,
            status="error",
            error_message=error_message,
        )
        return campaign_id, False, None  # Campaign failed, so ad won't be created

    # If campaign creation was successful and ad details are provided, publish the ad
    if campaign_success and ad_title and ad_target_url and publisher_id:
        try:
            ad_api_response = api_create_ad(
                title=ad_title,
                targetUrl=ad_target_url,
                description=ad_description,
                imageUrl=ad_image_url,
                status=ad_status,
                campaignId=publisher_id,
            )
            # Extract ad data from the nested response structure
            created_ad_data = ad_api_response.get("ad", {})

            # Update the campaign's publisher_data with this new ad information
            if (
                campaign_api_response
            ):  # Should always be true if campaign_success is true
                if "ads" not in campaign_api_response:
                    campaign_api_response["ads"] = []
                campaign_api_response["ads"].append(ad_api_response)

                await update_campaign_publisher_data(
                    session, campaign_id, publisher_id, campaign_api_response
                )
            
            # Process ad data for return
            ad_data = {}
            if created_ad_data:
                ad_data = {
                    "id": created_ad_data.get("id", "unknown"),
                    "title": created_ad_data.get("title", ad_title),
                    "description": created_ad_data.get("description", ad_description),
                    "status": created_ad_data.get("status", ad_status or "active"),
                    "targetUrl": created_ad_data.get("targetUrl", ad_target_url),
                    "imageUrl": created_ad_data.get("imageUrl", ad_image_url),
                    "createdAt": created_ad_data.get("createdAt", ""),
                    "updatedAt": created_ad_data.get("updatedAt", ""),
                    "metrics": created_ad_data.get("metrics", {}),
                }
            # No separate success flag for ad, its presence in ad_data indicates success

        except AdPublisherError as e:
            # Ad creation failed, but campaign was successful.
            # Log error, but don't change campaign status from "active".
            # The ad_data will remain None.
            error_message = str(e)
            logger.error(
                f"Error creating ad in API for campaign {campaign_id}: {error_message}"
            )
            # Optionally, we could store this ad creation error in the campaign's data
            # For now, we just log it and ad_data remains None.

    return campaign_id, campaign_success, ad_data


async def update_campaign(session: AsyncSession, campaign_id: str, **kwargs) -> bool:
    """
    Update a campaign in our database.

    Args:
        session: Database session
        campaign_id: ID of the campaign to update
        **kwargs: Fields to update

    Returns:
        Success flag
    """
    from database_storage import update_campaign as db_update_campaign

    return await db_update_campaign(session, campaign_id, **kwargs)


async def get_all_campaigns(
    session: AsyncSession,
    conversation_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get all campaigns, optionally filtered by conversation.

    Args:
        session: Database session
        conversation_id: Optional conversation ID to filter by

    Returns:
        List of campaign dictionaries
    """
    from database_storage import get_conversation_campaigns

    if conversation_id:
        return await get_conversation_campaigns(session, conversation_id)

    # If no conversation_id, we'd need to implement a get_all function
    # For now, this is a placeholder that would need to be implemented
    # in the database layer
    return []


async def get_campaign_by_id(
    session: AsyncSession,
    campaign_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Get a campaign by ID.

    Args:
        session: Database session
        campaign_id: ID of the campaign to retrieve

    Returns:
        Campaign dictionary or None if not found
    """
    return await get_campaign(session, campaign_id)
