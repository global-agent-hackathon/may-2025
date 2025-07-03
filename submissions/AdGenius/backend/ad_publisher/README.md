# Ad Publisher Module

## Overview

This module (`backend/ad_publisher`) is responsible for integrating with an external Ad Publisher API. It provides functionalities to create advertising campaigns and individual ads within the publisher's platform.

The integration follows a domain-driven design approach and includes a suite of unit tests to ensure reliability. The module handles the nested response structure from the API, where campaign and ad data are returned in objects under `campaign` and `ad` keys respectively.

## Features

- Create new advertising campaigns.
- Create new ads within a specified campaign.
- Handles API authentication using an API key.
- Custom error handling for various HTTP status codes (400, 401, 403, 404, 500).
- Service layer for campaign and ad publishing with database integration.
- Storage of campaign and ad data in the database.

## Configuration

To use this module, you need to set the following environment variable:

- `AD_PUBLISHER_API_KEY`: Your API key for the Ad Publisher service.

The module will read this key to authenticate requests to the Ad Publisher API. Ensure this variable is set in the environment where the backend application is running.

## API Base URL

The API client in `ad_publisher.py` uses the base URL: `https://ads-publisher.feedmob.ai/api/v1`. You must ensure this is the correct base URL for your Ad Publisher service.

## Usage

### Direct API Functions

The primary API functions provided by this module are:

- `create_campaign(name: str, startDate: str, description: Optional[str], endDate: Optional[str], status: Optional[str], budget: Optional[float]) -> Dict[str, Dict[str, Any]]`: Creates a new campaign in the Ad Publisher platform and returns a nested response with campaign data under the 'campaign' key.
- `create_ad(title: str, targetUrl: str, description: Optional[str], imageUrl: Optional[str], status: Optional[str], campaignId: Optional[str]) -> Dict[str, Dict[str, Any]]`: Creates a new ad within an existing campaign in the Ad Publisher platform and returns a nested response with ad data under the 'ad' key.

### Service Layer Functions

The service layer provides database integration for campaign and ad management:

- `publish_campaign(session, conversation_id, campaign_name, product_name, product_url, start_date, ...) -> Tuple[str, bool]`: Creates a campaign in both the database and the Ad Publisher API.
- `publish_ad(session, campaign_id, title, target_url, ...) -> Tuple[bool, Optional[Dict]]`: Creates an ad for an existing campaign in the Ad Publisher API.
- `get_all_campaigns(session, conversation_id) -> List[Dict]`: Retrieves campaigns with optional filtering by conversation.
- `get_campaign_by_id(session, campaign_id) -> Optional[Dict]`: Retrieves a specific campaign by ID.
- `update_campaign(session, campaign_id, **kwargs) -> bool`: Updates campaign properties in the database.

### Examples

#### Direct API Example

```python
# Ensure AD_PUBLISHER_API_KEY is set in your environment
# and the API_BASE_URL in ad_publisher.py is correct.

from ad_publisher.ad_publisher import create_campaign, create_ad, AdPublisherError

# Example: Create a campaign
try:
    campaign_data = {
        "name": "Summer Sale Campaign",
        "startDate": "2024-07-01",
        "endDate": "2024-07-31",
        "budget": 1000.00
    }
    campaign_response = create_campaign(**campaign_data)
    print(f"Campaign created successfully: {campaign_response}")

    # Access the campaign information from the nested response
    campaign_id = campaign_response["campaign"]["id"]
    campaign_name = campaign_response["campaign"]["name"]
    print(f"Campaign ID: {campaign_id}, Name: {campaign_name}")

    # Example: Create an ad for the new campaign
    ad_data = {
        "title": "Summer Sale Ad",
        "targetUrl": "http://example.com/summer-sale",
        "description": "Get 50% off on all summer items",
        "imageUrl": "http://example.com/creative.jpg",
        "campaignId": campaign_id
    }
    ad_response = create_ad(**ad_data)
    print(f"Ad created successfully: {ad_response}")

    # Access the ad information from the nested response
    ad_id = ad_response["ad"]["id"]
    ad_title = ad_response["ad"]["title"]
    ad_metrics = ad_response["ad"]["metrics"]
    print(f"Ad ID: {ad_id}, Title: {ad_title}")
    print(f"Initial Ad Metrics: {ad_metrics}")

except AdPublisherError as e:
    print(f"An error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

#### Service Layer Example

```python
# Example usage of the service layer with database integration
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from ad_publisher.service import publish_campaign_and_ad
from database_storage import get_session

async def create_campaign_and_ad():
    async for session in get_session():
        # Create and publish a campaign with ad
        campaign_id, success, ad_data = await publish_campaign_and_ad(
            session=session,
            conversation_id="conversation-123",
            campaign_name="Summer Sale Campaign",
            product_name="Beach Accessories",
            product_url="http://example.com/beach",
            start_date="2024-07-01",
            campaign_description="Seasonal sale for summer products",
            campaign_end_date="2024-07-31",
            campaign_budget=1000.00,
            campaign_status="active",
            campaign_image_url="http://example.com/images/campaign.jpg",
            ad_title="50% Off Beach Umbrellas",
            ad_target_url="http://example.com/beach/umbrellas",
            ad_description="Limited time offer on premium beach umbrellas",
            ad_image_url="http://example.com/images/umbrella.jpg",
            ad_status="active"
        )

        if success:
            print(f"Campaign published successfully with ID: {campaign_id}")

            if ad_data:
                print(f"Ad published successfully: {ad_data}")
                print(f"Ad ID: {ad_data.get('id')}")
                print(f"Ad metrics: {ad_data.get('metrics', {})}")
            else:
                print("Campaign created but no ad was published")
        else:
            print(f"Campaign creation failed, but saved in database with ID: {campaign_id}")

# Run the async function
asyncio.run(create_campaign_and_ad())
```

(These examples might be placed in an `examples.py` file or used directly in your application code.)

## Testing

Unit tests are provided for both the API layer (`test_ad_publisher.py`) and the service layer (`test_service.py`). The tests use the `unittest` and `pytest` frameworks. To run the tests:

1.  Ensure you are in the root directory of the project.
2.  Make sure `uv` is installed and available.
3.  Run the following commands:

    ```bash
    # Run API layer tests
    uv run -m unittest backend.ad_publisher.test_ad_publisher

    # Run service layer tests
    uv run -m pytest backend/ad_publisher/test_service.py
    ```

    Alternatively, if your test runner is configured differently, adapt the command accordingly (e.g., `python -m unittest backend/ad_publisher/test_ad_publisher.py`).

The tests mock external HTTP requests, database sessions, and environment variables, so they can be run without a live API key, database, or network connection.

## Error Handling

The module defines custom exceptions to handle specific API error responses:

- `BadRequestError` (400)
- `UnauthorizedError` (401)
- `ForbiddenError` (403)
- `NotFoundError` (404)
- `ServerError` (500)
- `AdPublisherError` (for other client-side or unexpected errors)

### API Layer Error Handling

When calling the API functions directly, catch these exceptions to handle API issues gracefully in your application.

### Service Layer Error Handling

The service layer handles API errors internally and provides error information through:

1. Return values (boolean success flags)
2. Campaign status updates in the database (setting status to "error" with error message)
3. Logging of error details

This allows for graceful handling of API issues while preserving campaign data in the database.

## Database Integration

The service layer interacts with the database to:

1. Store campaign and ad information before attempting API calls
2. Update campaign status based on API results
3. Store publisher-assigned IDs and response data
4. Handle error scenarios with appropriate status updates

This approach ensures data integrity even when the external API experiences issues.

