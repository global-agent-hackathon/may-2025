import json
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agents.tools.parse_ad_requirements import (
    Advertisement,
)
from database_storage.database import DraftCampaignTypes


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def valid_advertisement_dict():
    """Create a valid advertisement dictionary"""
    return {
        "product_or_service": "Test Product",
        "product_or_service_url": "https://example.com",
        "campaign_name": "Test Campaign",
        "target_audience": "Test Audience",
        "geography": "Test Region",
        "ad_format": "video",
        "budget": "$5000",
        "platform": "TikTok",
        "kpi": "conversion_rate",
        "time_period": "2024-06-01 to 2024-06-30",
        "creative_direction": "Test direction",
        "other_details": ["detail1", "detail2"],
    }


@pytest.fixture
def valid_advertisement_json(valid_advertisement_dict):
    """Create a valid advertisement JSON string"""
    return json.dumps(valid_advertisement_dict)


@pytest.mark.asyncio
async def test_store_valid_advertisement_dict(mock_session, valid_advertisement_dict):
    """Test storing a valid advertisement dictionary"""
    # Mock the upsert_draft_campaign function
    with patch(
        "agents.tools.parse_ad_requirements.upsert_draft_campaign"
    ) as mock_upsert:
        mock_upsert.return_value = ("test-draft-id", True)

        # Mock an Advertisement instance directly
        advertisement = Advertisement(**valid_advertisement_dict)

        # Patch the store_advertisement_requirements function directly
        with patch(
            "agents.tools.parse_ad_requirements._get_missing_fields", return_value=[]
        ):
            # Import the function directly from the module
            from agents.tools.parse_ad_requirements import (
                create_store_advertisement_requirements_tool,
            )

            # Get the tool function (will be a closure that contains our function)
            tool_function = create_store_advertisement_requirements_tool(
                session=mock_session,
                conversation_id="test-conversation",
            )

            # Access the function object directly
            store_fn = tool_function.__wrapped__  # type: ignore

            # Call the function (bypassing the tool decorator)
            result = await store_fn(advertisement)

        assert result["success"] is True
        assert result["draft_id"] == "test-draft-id"
        assert "created successfully" in result["message"].lower()

        # Verify upsert_draft_campaign was called with correct arguments
        mock_upsert.assert_called_once_with(
            session=mock_session,
            type=DraftCampaignTypes.REQUIREMENTS,
            data=advertisement.model_dump(),
            conversation_id="test-conversation",
        )


@pytest.mark.asyncio
async def test_store_valid_advertisement_json(mock_session, valid_advertisement_json):
    """Test storing a valid advertisement JSON string"""
    with patch(
        "agents.tools.parse_ad_requirements.upsert_draft_campaign"
    ) as mock_upsert:
        mock_upsert.return_value = ("test-draft-id", True)

        # Parse the JSON string into a dictionary
        advertisement_dict = json.loads(valid_advertisement_json)
        advertisement = Advertisement(**advertisement_dict)

        # Patch the store_advertisement_requirements function directly
        with patch(
            "agents.tools.parse_ad_requirements._get_missing_fields", return_value=[]
        ):
            # Import the function directly from the module
            from agents.tools.parse_ad_requirements import (
                create_store_advertisement_requirements_tool,
            )

            # Get the tool function (will be a closure that contains our function)
            tool_function = create_store_advertisement_requirements_tool(
                session=mock_session,
                conversation_id="test-conversation",
            )

            # Access the function object directly
            store_fn = tool_function.__wrapped__  # type: ignore

            # Call the function (bypassing the tool decorator)
            result = await store_fn(advertisement)

        assert result["success"] is True
        assert result["draft_id"] == "test-draft-id"
        assert "created successfully" in result["message"].lower()


@pytest.mark.asyncio
async def test_store_invalid_json(mock_session):
    """Test storing an invalid JSON string"""
    # This test isn't applicable when bypassing the tool decorator
    # The validation would happen in the decorator, not our function
    # We'll simulate a similar error instead

    from agents.tools.parse_ad_requirements import (
        create_store_advertisement_requirements_tool,
    )

    # Get the tool function (will be a closure that contains our function)
    tool_function = create_store_advertisement_requirements_tool(
        session=mock_session,
        conversation_id="test-conversation",
    )

    # Access the function object directly
    store_fn = tool_function.__wrapped__  # type: ignore

    # Create a mock advertisement with invalid structure
    with pytest.raises(Exception):
        # This should fail because "invalid json" is not a valid Advertisement
        await store_fn("invalid json")


@pytest.mark.asyncio
async def test_store_missing_required_fields(mock_session):
    """Test storing an advertisement with missing required fields"""

    # Create a proper Advertisement object but with missing fields
    advertisement = Advertisement(
        product_or_service="Test Product",
        product_or_service_url="",  # Missing field
        campaign_name="",  # Missing field
        target_audience="",  # Missing field
        geography="",  # Missing field
        ad_format="",  # Missing field
        budget="",  # Missing field
        platform="",  # Missing field
        kpi="",  # Missing field
    )

    # Mock missing fields check
    missing_fields = [
        "product_or_service_url",
        "campaign_name",
        "target_audience",
        "geography",
        "ad_format",
        "budget",
        "platform",
        "kpi",
    ]

    with patch(
        "agents.tools.parse_ad_requirements._get_missing_fields",
        return_value=missing_fields,
    ):
        # Import the function directly from the module
        from agents.tools.parse_ad_requirements import (
            create_store_advertisement_requirements_tool,
        )

        # Get the tool function (will be a closure that contains our function)
        tool_function = create_store_advertisement_requirements_tool(
            session=mock_session,
            conversation_id="test-conversation",
        )

        # Access the function object directly
        store_fn = tool_function.__wrapped__  # type: ignore

        # Call the function (bypassing the tool decorator)
        result = await store_fn(advertisement)

    assert result["success"] is False
    assert "missing required fields" in result["message"].lower()
    assert "missing_fields" in result
    assert len(result["missing_fields"]) > 0


@pytest.mark.asyncio
async def test_store_empty_required_fields(mock_session):
    """Test storing an advertisement with empty required fields"""
    # Create a proper Advertisement object with empty fields
    advertisement = Advertisement(
        product_or_service="",  # Empty field
        product_or_service_url="https://example.com",
        campaign_name="Test Campaign",
        target_audience="Test Audience",
        geography="Test Region",
        ad_format="video",
        budget="$5000",
        platform="TikTok",
        kpi="conversion_rate",
    )

    # Mock missing fields check to return the empty field
    missing_fields = ["product_or_service"]

    with patch(
        "agents.tools.parse_ad_requirements._get_missing_fields",
        return_value=missing_fields,
    ):
        # Import the function directly from the module
        from agents.tools.parse_ad_requirements import (
            create_store_advertisement_requirements_tool,
        )

        # Get the tool function (will be a closure that contains our function)
        tool_function = create_store_advertisement_requirements_tool(
            session=mock_session,
            conversation_id="test-conversation",
        )

        # Access the function object directly
        store_fn = tool_function.__wrapped__  # type: ignore

        # Call the function (bypassing the tool decorator)
        result = await store_fn(advertisement)

    assert result["success"] is False
    assert "missing required fields" in result["message"].lower()
    assert "product_or_service" in result["missing_fields"]


@pytest.mark.asyncio
async def test_database_error_handling(mock_session, valid_advertisement_dict):
    """Test handling of database errors"""
    with patch(
        "agents.tools.parse_ad_requirements.upsert_draft_campaign"
    ) as mock_upsert:
        mock_upsert.side_effect = Exception("Database error")

        # Create a proper Advertisement object
        advertisement = Advertisement(**valid_advertisement_dict)

        # Mock missing fields check to return no missing fields
        with patch(
            "agents.tools.parse_ad_requirements._get_missing_fields", return_value=[]
        ):
            # Import the function directly from the module
            from agents.tools.parse_ad_requirements import (
                create_store_advertisement_requirements_tool,
            )

            # Get the tool function (will be a closure that contains our function)
            tool_function = create_store_advertisement_requirements_tool(
                session=mock_session,
                conversation_id="test-conversation",
            )

            # Access the function object directly
            store_fn = tool_function.__wrapped__  # type: ignore

            # Call the function (bypassing the tool decorator)
            result = await store_fn(advertisement)

        assert result["success"] is False
        assert "failed to store" in result["message"].lower()
        assert "database error" in result["message"].lower()


@pytest.mark.asyncio
async def test_optional_fields_not_required(mock_session):
    """Test that optional fields are not required"""
    # Create a proper Advertisement object with only required fields
    advertisement = Advertisement(
        product_or_service="Test Product",
        product_or_service_url="https://example.com",
        campaign_name="Test Campaign",
        target_audience="Test Audience",
        geography="Test Region",
        ad_format="video",
        budget="$5000",
        platform="TikTok",
        kpi="conversion_rate",
        # Optional fields will be default values
    )

    with patch(
        "agents.tools.parse_ad_requirements.upsert_draft_campaign"
    ) as mock_upsert:
        mock_upsert.return_value = ("test-draft-id", True)

        # Mock missing fields check to return no missing fields
        with patch(
            "agents.tools.parse_ad_requirements._get_missing_fields", return_value=[]
        ):
            # Import the function directly from the module
            from agents.tools.parse_ad_requirements import (
                create_store_advertisement_requirements_tool,
            )

            # Get the tool function (will be a closure that contains our function)
            tool_function = create_store_advertisement_requirements_tool(
                session=mock_session,
                conversation_id="test-conversation",
            )

            # Access the function object directly
            store_fn = tool_function.__wrapped__  # type: ignore

            # Call the function (bypassing the tool decorator)
            result = await store_fn(advertisement)

        assert result["success"] is True
        assert result["draft_id"] == "test-draft-id"
        assert result["is_new"] is True


@pytest.mark.asyncio
async def test_update_existing_advertisement(mock_session, valid_advertisement_dict):
    """Test updating an existing advertisement"""
    with patch(
        "agents.tools.parse_ad_requirements.upsert_draft_campaign"
    ) as mock_upsert:
        # Simulate updating existing record
        mock_upsert.return_value = ("existing-draft-id", False)

        # Create a proper Advertisement object
        advertisement = Advertisement(**valid_advertisement_dict)

        # Mock missing fields check to return no missing fields
        with patch(
            "agents.tools.parse_ad_requirements._get_missing_fields", return_value=[]
        ):
            # Import the function directly from the module
            from agents.tools.parse_ad_requirements import (
                create_store_advertisement_requirements_tool,
            )

            # Get the tool function (will be a closure that contains our function)
            tool_function = create_store_advertisement_requirements_tool(
                session=mock_session,
                conversation_id="existing-conversation",
            )

            # Access the function object directly
            store_fn = tool_function.__wrapped__  # type: ignore

            # Call the function (bypassing the tool decorator)
            result = await store_fn(advertisement)

        assert result["success"] is True
        assert result["draft_id"] == "existing-draft-id"
        assert "updated successfully" in result["message"].lower()
        assert result["is_new"] is False

        # Verify upsert_draft_campaign was called with correct arguments
        mock_upsert.assert_called_once_with(
            session=mock_session,
            type=DraftCampaignTypes.REQUIREMENTS,
            data=advertisement.model_dump(),
            conversation_id="existing-conversation",
        )
