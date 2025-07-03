"""
Package for interacting with the Ad Publisher API.

This package provides functions to create campaigns and advertisements
through the Ad Publisher API endpoints, as well as services to manage
campaign and ad publishing with database integration.
"""

# Direct API functions
from .ad_publisher import (
    create_campaign as api_create_campaign,
    create_ad as api_create_ad,
    AdPublisherError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ServerError,
)

# Service layer functions
from .service import (
    publish_campaign_and_ad,
    update_campaign,
    get_all_campaigns,
    get_campaign_by_id,
)

__all__ = [
    # Direct API functions
    "api_create_campaign",
    "api_create_ad",
    "AdPublisherError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ServerError",
    
    # Service layer functions
    "publish_campaign_and_ad",
    "update_campaign",
    "get_all_campaigns",
    "get_campaign_by_id",
]