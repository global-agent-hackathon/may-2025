import os
from typing import Any, Dict, Optional

import requests


class AdPublisherError(Exception):
    """Base exception for all ad publisher errors."""

    pass


class ApiError(AdPublisherError):
    """Exception raised for API errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error ({status_code}): {message}")


class MissingApiKeyError(AdPublisherError):
    """Exception raised when API key is not set."""

    def __init__(self):
        super().__init__("AD_PUBLISHER_API_KEY not set in environment variables")


class BadRequestError(ApiError):
    """Exception raised for 400 Bad Request errors."""

    def __init__(self, message: str = "Missing required fields"):
        super().__init__(400, message)


class UnauthorizedError(ApiError):
    """Exception raised for 401 Unauthorized errors."""

    def __init__(self, message: str = "Unauthorized - Invalid API key"):
        super().__init__(401, message)


class ForbiddenError(ApiError):
    """Exception raised for 403 Forbidden errors."""

    def __init__(self, message: str = "Forbidden - Campaign does not belong to user"):
        super().__init__(403, message)


class NotFoundError(ApiError):
    """Exception raised for 404 Not Found errors."""

    def __init__(self, message: str = "Campaign not found"):
        super().__init__(404, message)


class ServerError(ApiError):
    """Exception raised for 500 Server errors."""

    def __init__(self, message: str = "Server error"):
        super().__init__(500, message)


def get_api_key() -> str:
    """
    Get the Ad Publisher API key from environment variables.

    Returns:
        str: The API key.

    Raises:
        MissingApiKeyError: If the API key is not set.
    """
    api_key = os.getenv("AD_PUBLISHER_API_KEY")
    if not api_key:
        raise MissingApiKeyError()
    return api_key


def get_base_headers() -> Dict[str, str]:
    """
    Get the base headers for API requests.

    Returns:
        Dict[str, str]: The headers dictionary.
    """
    return {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }


def handle_response(response: requests.Response) -> Dict[str, Dict[str, Any]]:
    """
    Handle the API response and raise appropriate exceptions.

    Args:
        response (requests.Response): The response from the API.

    Returns:
        Dict[str, Any]: The JSON response.

    Raises:
        BadRequestError: If the API returns a 400 error.
        UnauthorizedError: If the API returns a 401 error.
        ForbiddenError: If the API returns a 403 error.
        NotFoundError: If the API returns a 404 error.
        ServerError: If the API returns a 500 error.
        ApiError: For other status codes.
    """
    if response.status_code in (200, 201):
        return response.json()

    error_handlers = {
        400: BadRequestError,
        401: UnauthorizedError,
        403: ForbiddenError,
        404: NotFoundError,
        500: ServerError,
    }

    error_class = error_handlers.get(response.status_code)
    if error_class:
        # Try to extract error message from response if available
        try:
            error_message = response.json().get("message", None)
            if error_message:
                raise error_class(error_message)
        except Exception:
            raise error_class()
        raise error_class()

    # For unexpected status codes
    response.raise_for_status()
    raise ApiError(response.status_code, "Unexpected error")


def create_campaign(
    name: str,
    startDate: str,
    description: Optional[str] = None,
    endDate: Optional[str] = None,
    status: Optional[str] = None,
    budget: Optional[float] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Create a new campaign via the Ad Publisher API.

    Args:
        name (str): Campaign name (required).
        startDate (str): Campaign start date in ISO format (required).
        description (str, optional): Campaign description.
        endDate (str, optional): Campaign end date in ISO format.
        status (str, optional): Campaign status (draft, active, paused, completed).
        budget (float, optional): Campaign budget amount.

    Returns:
        Dict[str, Any]: The created campaign data with structure:
        {
            'campaign': {
                'id': str,
                'name': str,
                'description': str,
                'startDate': str,
                'endDate': str,
                'status': str,
                'createdAt': str,
                'updatedAt': str,
                'userId': str,
                'budget': {
                    'id': str,
                    'amount': float,
                    'spent': float,
                    'currency': str,
                    'createdAt': str,
                    'updatedAt': str,
                    'campaignId': str
                }
            }
        }

    Raises:
        Various ApiError exceptions for different error cases.
    """
    url = "https://ads-publisher.feedmob.ai/api/v1/campaigns"

    payload = {"name": name, "startDate": startDate}

    # Add optional fields if provided
    if description is not None:
        payload["description"] = description
    if endDate is not None:
        payload["endDate"] = endDate
    if status is not None:
        payload["status"] = status
    if budget is not None:
        payload["budget"] = str(budget)

    response = requests.post(url, json=payload, headers=get_base_headers())

    return handle_response(response)


def create_ad(
    title: str,
    targetUrl: str,
    description: Optional[str] = None,
    imageUrl: Optional[str] = None,
    status: Optional[str] = None,
    campaignId: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Create a new advertisement via the Ad Publisher API.

    Args:
        title (str): Advertisement title (required).
        targetUrl (str): Target URL for the advertisement (required).
        description (str, optional): Advertisement description.
        imageUrl (str, optional): URL to the advertisement image.
        status (str, optional): Advertisement status (draft, active, paused).
        campaignId (str, optional): ID of the campaign this ad belongs to.

    Returns:
        Dict[str, Any]: The created advertisement data with structure:
        {
            'ad': {
                'id': str,
                'title': str,
                'description': str,
                'imageUrl': str,
                'targetUrl': str,
                'status': str,
                'createdAt': str,
                'updatedAt': str,
                'userId': str,
                'campaignId': str,
                'metrics': {
                    'id': str,
                    'impressions': int,
                    'clicks': int,
                    'conversions': int,
                    'createdAt': str,
                    'updatedAt': str,
                    'advertisementId': str
                },
                'campaign': {
                    'id': str,
                    'name': str
                }
            }
        }

    Raises:
        Various ApiError exceptions for different error cases.
    """
    url = "https://ads-publisher.feedmob.ai/api/v1/ads"

    payload = {"title": title, "targetUrl": targetUrl}

    # Add optional fields if provided
    if description is not None:
        payload["description"] = description
    if imageUrl is not None:
        payload["imageUrl"] = imageUrl
    if status is not None:
        payload["status"] = status
    if campaignId is not None:
        payload["campaignId"] = campaignId

    response = requests.post(url, json=payload, headers=get_base_headers())

    return handle_response(response)


# uv run -m ad_publisher.ad_publisher
if __name__ == "__main__":
    try:
        # Create a test campaign
        campaign = create_campaign(
            name="Test Campaign",
            startDate="2023-10-01T00:00:00Z",
            description="This is a test campaign",
            endDate="2023-10-31T23:59:59Z",
            status="draft",
            budget=1000.0,
        )
        print("Campaign created:", campaign)

        # Extract campaign details from the nested response structure
        campaign_id = campaign["campaign"]["id"]
        campaign_name = campaign["campaign"]["name"]

        print(f"Campaign ID: {campaign_id}")
        print(f"Campaign Name: {campaign_name}")

        # Create a test ad in the campaign
        ad = create_ad(
            title="Test Ad",
            targetUrl="https://example.com/test-ad",
            description="This is a test ad",
            imageUrl="https://example.com/test-ad-image.jpg",
            status="draft",
            campaignId=campaign_id,
        )
        print("Ad created:", ad)

        # Extract ad details from the nested response structure
        ad_id = ad["ad"]["id"]
        ad_title = ad["ad"]["title"]

        print(f"Ad ID: {ad_id}")
        print(f"Ad Title: {ad_title}")
        print(f"Ad Metrics: {ad['ad']['metrics']}")
    except AdPublisherError as e:
        print(f"Error: {e}")
