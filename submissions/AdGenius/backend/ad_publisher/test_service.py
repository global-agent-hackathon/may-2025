import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ad_publisher.ad_publisher import AdPublisherError
from ad_publisher.service import publish_campaign_and_ad


@pytest.mark.asyncio
async def test_successful_campaign_without_ad():
    """
    Test case for publishing a campaign successfully without an ad.
    """
    # Setup mocks
    mock_session = AsyncMock()
    mock_db_create_campaign = AsyncMock(return_value="mock-campaign-id")
    mock_update_campaign = AsyncMock(return_value=True)
    mock_update_publisher_data = AsyncMock()
    mock_api_create_campaign = MagicMock(
        return_value={"campaign": {"id": "mock-publisher-id", "status": "active"}}
    )

    # Patch the necessary functions
    with patch(
        "ad_publisher.service.db_create_campaign", mock_db_create_campaign
    ), patch(
        "ad_publisher.service.update_campaign", mock_update_campaign
    ), patch(
        "ad_publisher.service.update_campaign_publisher_data", mock_update_publisher_data
    ), patch(
        "ad_publisher.service.api_create_campaign", mock_api_create_campaign
    ):
        # Call the function under test
        campaign_id, success, ad_data = await publish_campaign_and_ad(
            session=mock_session,
            conversation_id="mock-conversation-id",
            campaign_name="Test Campaign",
            product_name="Test Product",
            product_url="https://example.com/product",
            start_date="2023-01-01",
            campaign_description="Test Description",
            campaign_end_date="2023-12-31",
            campaign_status="active",
            campaign_budget=1000.0,
            campaign_image_url="https://example.com/image.jpg",
            # No ad parameters provided
        )

        # Assertions
        assert campaign_id == "mock-campaign-id"
        assert success is True
        assert ad_data is None
        
        # Verify all expected functions were called with correct parameters
        mock_db_create_campaign.assert_called_once()
        mock_api_create_campaign.assert_called_once_with(
            name="Test Campaign",
            startDate="2023-01-01",
            description="Test Description",
            endDate="2023-12-31",
            status="active",
            budget=1000.0,
        )
        mock_update_publisher_data.assert_called_once_with(
            mock_session, "mock-campaign-id", "mock-publisher-id", {"campaign": {"id": "mock-publisher-id", "status": "active"}}
        )
        # Verify campaign status was updated to active
        mock_update_campaign.assert_called_with(mock_session, "mock-campaign-id", status="active")


@pytest.mark.asyncio
async def test_successful_campaign_with_ad():
    """
    Test case for publishing a campaign and an ad successfully.
    """
    # Setup mocks
    mock_session = AsyncMock()
    mock_db_create_campaign = AsyncMock(return_value="mock-campaign-id")
    mock_update_campaign = AsyncMock(return_value=True)
    mock_update_publisher_data = AsyncMock()
    mock_api_create_campaign = MagicMock(
        return_value={"campaign": {"id": "mock-publisher-id", "status": "active"}}
    )
    mock_api_create_ad = MagicMock(
        return_value={"ad": {"id": "mock-ad-id", "status": "active"}}
    )

    # Patch the necessary functions
    with patch(
        "ad_publisher.service.db_create_campaign", mock_db_create_campaign
    ), patch(
        "ad_publisher.service.update_campaign", mock_update_campaign
    ), patch(
        "ad_publisher.service.update_campaign_publisher_data", mock_update_publisher_data
    ), patch(
        "ad_publisher.service.api_create_campaign", mock_api_create_campaign
    ), patch(
        "ad_publisher.service.api_create_ad", mock_api_create_ad
    ):
        # Call the function under test
        campaign_id, success, ad_data = await publish_campaign_and_ad(
            session=mock_session,
            conversation_id="mock-conversation-id",
            campaign_name="Test Campaign",
            product_name="Test Product",
            product_url="https://example.com/product",
            start_date="2023-01-01",
            campaign_description="Test Description",
            campaign_end_date="2023-12-31",
            campaign_status="active",
            campaign_budget=1000.0,
            campaign_image_url="https://example.com/image.jpg",
            # Ad parameters
            ad_title="Test Ad",
            ad_target_url="https://example.com/ad",
            ad_description="Test Ad Description",
            ad_image_url="https://example.com/ad-image.jpg",
            ad_status="active",
        )

        # Assertions
        assert campaign_id == "mock-campaign-id"
        assert success is True
        assert ad_data.get("id") == "mock-ad-id"
        assert ad_data.get("status") == "active"
        assert "title" in ad_data
        assert "description" in ad_data
        assert "metrics" in ad_data
        
        # Verify all expected functions were called with correct parameters
        mock_db_create_campaign.assert_called_once()
        mock_api_create_campaign.assert_called_once()
        mock_api_create_ad.assert_called_once_with(
            title="Test Ad",
            targetUrl="https://example.com/ad",
            description="Test Ad Description",
            imageUrl="https://example.com/ad-image.jpg",
            status="active",
            campaignId="mock-publisher-id",
        )
        
        # Verify update_publisher_data was called twice (once for campaign, once for ad)
        assert mock_update_publisher_data.call_count == 2
        
        # Verify the last update includes the ad data
        expected_data = {"campaign": {"id": "mock-publisher-id", "status": "active"}, "ads": [{"ad": {"id": "mock-ad-id", "status": "active"}}]}
        mock_update_publisher_data.assert_called_with(
            mock_session, "mock-campaign-id", "mock-publisher-id", expected_data
        )


@pytest.mark.asyncio
async def test_failed_campaign_creation():
    """
    Test case for failed campaign creation.
    """
    # Setup mocks
    mock_session = AsyncMock()
    mock_db_create_campaign = AsyncMock(return_value="mock-campaign-id")
    mock_update_campaign = AsyncMock(return_value=True)
    mock_api_create_campaign = MagicMock(side_effect=AdPublisherError("API Error"))

    # Patch the necessary functions
    with patch(
        "ad_publisher.service.db_create_campaign", mock_db_create_campaign
    ), patch(
        "ad_publisher.service.update_campaign", mock_update_campaign
    ), patch(
        "ad_publisher.service.api_create_campaign", mock_api_create_campaign
    ):
        # Call the function under test
        campaign_id, success, ad_data = await publish_campaign_and_ad(
            session=mock_session,
            conversation_id="mock-conversation-id",
            campaign_name="Test Campaign",
            product_name="Test Product",
            product_url="https://example.com/product",
            start_date="2023-01-01",
            campaign_description="Test Description",
            # Include ad parameters, but they shouldn't be used
            ad_title="Test Ad",
            ad_target_url="https://example.com/ad",
        )

        # Assertions
        assert campaign_id == "mock-campaign-id"
        assert success is False
        assert ad_data is None
        
        # Verify the campaign was created in DB but update_campaign was called with error status
        mock_db_create_campaign.assert_called_once()
        mock_update_campaign.assert_called_once_with(
            mock_session, "mock-campaign-id", status="error", error_message="API Error"
        )


@pytest.mark.asyncio
async def test_campaign_missing_publisher_id():
    """
    Test case for a campaign API response missing publisher_id.
    """
    # Setup mocks
    mock_session = AsyncMock()
    mock_db_create_campaign = AsyncMock(return_value="mock-campaign-id")
    mock_update_campaign = AsyncMock(return_value=True)
    # API response without an ID
    mock_api_create_campaign = MagicMock(return_value={"campaign": {"status": "active"}})

    # Patch the necessary functions
    with patch(
        "ad_publisher.service.db_create_campaign", mock_db_create_campaign
    ), patch(
        "ad_publisher.service.update_campaign", mock_update_campaign
    ), patch(
        "ad_publisher.service.api_create_campaign", mock_api_create_campaign
    ):
        # Call the function under test
        campaign_id, success, ad_data = await publish_campaign_and_ad(
            session=mock_session,
            conversation_id="mock-conversation-id",
            campaign_name="Test Campaign",
            product_name="Test Product",
            product_url="https://example.com/product",
            start_date="2023-01-01",
        )

        # Assertions
        assert campaign_id == "mock-campaign-id"
        assert success is False
        assert ad_data is None
        
        # Verify update_campaign was called with error status
        mock_update_campaign.assert_called_once_with(
            mock_session, 
            "mock-campaign-id", 
            status="error", 
            error_message="API response missing campaign ID"
        )


@pytest.mark.asyncio
async def test_successful_campaign_failed_ad():
    """
    Test case for a successful campaign but failed ad creation.
    """
    # Setup mocks
    mock_session = AsyncMock()
    mock_db_create_campaign = AsyncMock(return_value="mock-campaign-id")
    mock_update_campaign = AsyncMock(return_value=True)
    mock_update_publisher_data = AsyncMock()
    mock_api_create_campaign = MagicMock(
        return_value={"campaign": {"id": "mock-publisher-id", "status": "active"}}
    )
    mock_api_create_ad = MagicMock(side_effect=AdPublisherError("Ad API Error"))

    # Patch the necessary functions
    with patch(
        "ad_publisher.service.db_create_campaign", mock_db_create_campaign
    ), patch(
        "ad_publisher.service.update_campaign", mock_update_campaign
    ), patch(
        "ad_publisher.service.update_campaign_publisher_data", mock_update_publisher_data
    ), patch(
        "ad_publisher.service.api_create_campaign", mock_api_create_campaign
    ), patch(
        "ad_publisher.service.api_create_ad", mock_api_create_ad
    ):
        # Call the function under test
        campaign_id, success, ad_data = await publish_campaign_and_ad(
            session=mock_session,
            conversation_id="mock-conversation-id",
            campaign_name="Test Campaign",
            product_name="Test Product",
            product_url="https://example.com/product",
            start_date="2023-01-01",
            # Ad parameters
            ad_title="Test Ad",
            ad_target_url="https://example.com/ad",
        )

        # Assertions
        assert campaign_id == "mock-campaign-id"
        assert success is True  # Campaign was still successful
        assert ad_data is None  # Ad failed, so data should be None
        
        # Verify campaign was updated to active despite ad failure
        mock_update_campaign.assert_called_with(mock_session, "mock-campaign-id", status="active")
        
        # Verify ad creation was attempted but failed
        mock_api_create_ad.assert_called_once()
        
        # Verify update_campaign_publisher_data was called only once (for campaign, not for ad)
        mock_update_publisher_data.assert_called_once()


@pytest.mark.asyncio
async def test_campaign_successful_partial_ad_details():
    """
    Test case where campaign is successful but ad creation is skipped due to missing ad details.
    """
    # Setup mocks
    mock_session = AsyncMock()
    mock_db_create_campaign = AsyncMock(return_value="mock-campaign-id")
    mock_update_campaign = AsyncMock(return_value=True)
    mock_update_publisher_data = AsyncMock()
    mock_api_create_campaign = MagicMock(
        return_value={"campaign": {"id": "mock-publisher-id", "status": "active"}}
    )
    mock_api_create_ad = MagicMock()

    # Patch the necessary functions
    with patch(
        "ad_publisher.service.db_create_campaign", mock_db_create_campaign
    ), patch(
        "ad_publisher.service.update_campaign", mock_update_campaign
    ), patch(
        "ad_publisher.service.update_campaign_publisher_data", mock_update_publisher_data
    ), patch(
        "ad_publisher.service.api_create_campaign", mock_api_create_campaign
    ), patch(
        "ad_publisher.service.api_create_ad", mock_api_create_ad
    ):
        # Call the function under test with only ad_title but missing ad_target_url
        campaign_id, success, ad_data = await publish_campaign_and_ad(
            session=mock_session,
            conversation_id="mock-conversation-id",
            campaign_name="Test Campaign",
            product_name="Test Product",
            product_url="https://example.com/product",
            start_date="2023-01-01",
            # Only provide ad_title but not ad_target_url
            ad_title="Test Ad",
        )

        # Assertions
        assert campaign_id == "mock-campaign-id"
        assert success is True
        assert ad_data is None
        
        # Verify ad creation was not attempted due to missing required parameters
        mock_api_create_ad.assert_not_called()
        
        # Verify campaign status was updated to active
        mock_update_campaign.assert_called_with(
            mock_session, "mock-campaign-id", status="active"
        )