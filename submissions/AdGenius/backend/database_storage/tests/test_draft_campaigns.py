import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database_storage.database import (
    DraftCampaignTypes,
    create_draft_campaign,
    delete_draft_campaign,
    get_conversation_draft_campaigns,
    get_draft_campaign,
    update_draft_campaign,
    upsert_draft_campaign,
)
from database_storage.repository.sqlite import DraftCampaignTable


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_draft_data():
    """Create sample draft campaign data"""
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
    }


@pytest.mark.asyncio
async def test_create_draft_campaign(mock_session, sample_draft_data):
    """Test creating a new draft campaign"""
    # Mock the session's add and commit methods
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()

    # Create the draft campaign
    await create_draft_campaign(
        session=mock_session,
        type=DraftCampaignTypes.REQUIREMENTS,
        data=sample_draft_data,
        conversation_id="test-conversation",
    )

    # Verify the draft was added to the session
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

    # Verify the draft object was created with correct data
    added_draft = mock_session.add.call_args[0][0]
    assert isinstance(added_draft, DraftCampaignTable)
    assert getattr(added_draft, "type") == "requirements"
    assert getattr(added_draft, "conversation_id") == "test-conversation"
    assert json.loads(getattr(added_draft, "data")) == sample_draft_data
    assert isinstance(added_draft.created_at, datetime)
    assert isinstance(added_draft.updated_at, datetime)


@pytest.mark.asyncio
async def test_get_draft_campaign(mock_session, sample_draft_data):
    """Test retrieving a draft campaign by ID"""
    # Create a mock draft campaign
    mock_draft = DraftCampaignTable(
        id="test-draft-id",
        type="requirements",
        data=json.dumps(sample_draft_data),
        conversation_id="test-conversation",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Mock the session's execute method to return our mock draft (sync chain)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_draft)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Get the draft campaign
    result = await get_draft_campaign(mock_session, "test-draft-id")

    # Verify the result
    assert result is not None
    assert result["id"] == "test-draft-id"
    assert result["type"] == "requirements"
    assert result["data"] == sample_draft_data
    assert result["conversation_id"] == "test-conversation"
    assert "created_at" in result
    assert "updated_at" in result


@pytest.mark.asyncio
async def test_get_nonexistent_draft_campaign(mock_session):
    """Test retrieving a non-existent draft campaign"""
    # Mock the session's execute method to return None (sync chain)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Get the draft campaign
    result = await get_draft_campaign(mock_session, "nonexistent-id")

    # Verify the result is None
    assert result is None


@pytest.mark.asyncio
async def test_get_conversation_draft_campaigns(mock_session, sample_draft_data):
    """Test retrieving draft campaigns for a conversation"""
    # Create mock draft campaigns
    mock_drafts = [
        DraftCampaignTable(
            id=f"test-draft-{i}",
            type="requirements",
            data=json.dumps(sample_draft_data),
            conversation_id="test-conversation",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        for i in range(3)
    ]

    # Mock the session's execute method for scalars().all() sync chain
    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=mock_drafts)
    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Get the draft campaigns
    results = await get_conversation_draft_campaigns(
        mock_session,
        conversation_id="test-conversation",
        type="requirements",
    )

    # Verify the results
    assert len(results) == 3
    for i, result in enumerate(results):
        assert result["id"] == f"test-draft-{i}"
        assert result["type"] == "requirements"
        assert result["data"] == sample_draft_data
        assert result["conversation_id"] == "test-conversation"


@pytest.mark.asyncio
async def test_update_draft_campaign(mock_session, sample_draft_data):
    """Test updating a draft campaign"""
    # Create a mock draft campaign
    mock_draft = DraftCampaignTable(
        id="test-draft-id",
        type="requirements",
        data=json.dumps(sample_draft_data),
        conversation_id="test-conversation",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Mock the session's execute method (sync chain)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_draft)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    # Update data
    updated_data = {**sample_draft_data, "budget": "$10000"}

    # Update the draft campaign
    success = await update_draft_campaign(
        mock_session,
        draft_id="test-draft-id",
        data=updated_data,
    )

    # Verify the update
    assert success is True
    assert json.loads(getattr(mock_draft, "data")) == updated_data
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_nonexistent_draft_campaign(mock_session):
    """Test updating a non-existent draft campaign"""
    # Mock the session's execute method to return None (sync chain)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Try to update the draft campaign
    success = await update_draft_campaign(
        mock_session,
        draft_id="nonexistent-id",
        data={"test": "data"},
    )

    # Verify the update failed
    assert success is False


@pytest.mark.asyncio
async def test_draft_campaign_repository_upsert_create(mock_session, sample_draft_data):
    """Test the repository upsert method when creating new draft"""
    from database_storage.repository.sqlite import SQLAlchemyDraftCampaignRepository

    # Create the repository
    repo = SQLAlchemyDraftCampaignRepository(mock_session)

    # Mock get_by_conversation to return empty list
    repo.get_by_conversation = AsyncMock(return_value=[])

    # Mock create method
    mock_draft_id = "new-repo-draft-id"
    repo.create = AsyncMock(return_value=mock_draft_id)
    repo.update = AsyncMock(return_value=True)  # Add this to avoid AttributeError

    # Test the upsert method
    draft_id, is_new = await repo.upsert(
        type="requirements", data=sample_draft_data, conversation_id="test-conversation"
    )

    # Verify results
    assert draft_id == mock_draft_id
    assert is_new is True

    # Verify create was called
    repo.create.assert_called_once_with(
        "requirements", sample_draft_data, "test-conversation"
    )

    # Verify update was not called
    repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_draft_campaign_repository_upsert_update(mock_session, sample_draft_data):
    """Test the repository upsert method when updating existing draft"""
    from database_storage.repository.sqlite import SQLAlchemyDraftCampaignRepository

    # Create the repository
    repo = SQLAlchemyDraftCampaignRepository(mock_session)

    # Create a mock existing draft
    existing_draft = {
        "id": "existing-repo-draft-id",
        "type": "requirements",
        "data": {"old_data": "value"},
        "conversation_id": "test-conversation",
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }

    # Mock get_by_conversation to return existing draft
    repo.get_by_conversation = AsyncMock(return_value=[existing_draft])

    # Mock update method
    repo.update = AsyncMock(return_value=True)
    repo.create = AsyncMock(
        return_value="should-not-be-called"
    )  # Add this to avoid AttributeError

    # Test the upsert method
    draft_id, is_new = await repo.upsert(
        type="requirements", data=sample_draft_data, conversation_id="test-conversation"
    )

    # Verify results
    assert draft_id == "existing-repo-draft-id"
    assert is_new is False

    # Verify update was called
    repo.update.assert_called_once_with("existing-repo-draft-id", sample_draft_data)

    # Verify create was not called
    repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_delete_draft_campaign(mock_session):
    """Test deleting a draft campaign"""
    # Create a mock draft campaign
    mock_draft = DraftCampaignTable(
        id="test-draft-id",
        type="requirements",
        data="{}",
        conversation_id="test-conversation",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Mock the session's execute and delete methods (sync chain)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_draft)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    # Delete the draft campaign
    success = await delete_draft_campaign(mock_session, "test-draft-id")

    # Verify the deletion
    assert success is True
    mock_session.delete.assert_called_once_with(mock_draft)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_nonexistent_draft_campaign(mock_session):
    """Test deleting a non-existent draft campaign"""
    # Mock the session's execute method to return None (sync chain)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Try to delete the draft campaign
    success = await delete_draft_campaign(mock_session, "nonexistent-id")

    # Verify the deletion failed
    assert success is False


@pytest.mark.asyncio
async def test_upsert_draft_campaign_create(mock_session, sample_draft_data):
    """Test upserting a draft campaign that doesn't exist (create new)"""
    # Mock the session's add and commit methods
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()

    # Mock the create function to return a specific draft ID
    mock_draft_id = "new-draft-id"

    # We need to mock the repository's upsert method that will be called
    mock_repo = MagicMock()
    mock_repo.draft_campaigns = MagicMock()
    mock_repo.draft_campaigns.upsert = AsyncMock(return_value=(mock_draft_id, True))
    # We don't need to mock these individual methods anymore since we're using upsert directly

    # Use patch to replace SQLAlchemyChatRepository instantiation
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "database_storage.database.SQLAlchemyChatRepository",
            lambda session: mock_repo,
        )

        # Call upsert_draft_campaign
        draft_id, is_new = await upsert_draft_campaign(
            session=mock_session,
            type=DraftCampaignTypes.REQUIREMENTS,
            data=sample_draft_data,
            conversation_id="test-conversation",
        )

        # Verify the result
        assert draft_id == mock_draft_id
        assert is_new is True

        # Verify upsert was called with correct parameters
        mock_repo.draft_campaigns.upsert.assert_called_once_with(
            "requirements", sample_draft_data, "test-conversation"
        )


@pytest.mark.asyncio
async def test_upsert_draft_campaign_update(mock_session, sample_draft_data):
    """Test upserting a draft campaign that already exists (update)"""
    existing_draft_id = "existing-draft-id"
    # Mock the repository's upsert to return an existing draft id with is_new=False
    mock_repo = MagicMock()
    mock_repo.draft_campaigns = MagicMock()
    mock_repo.draft_campaigns.upsert = AsyncMock(
        return_value=(existing_draft_id, False)
    )

    # Use patch to replace SQLAlchemyChatRepository instantiation
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "database_storage.database.SQLAlchemyChatRepository",
            lambda session: mock_repo,
        )

        # Call upsert_draft_campaign with new data
        draft_id, is_new = await upsert_draft_campaign(
            session=mock_session,
            type=DraftCampaignTypes.REQUIREMENTS,
            data=sample_draft_data,
            conversation_id="test-conversation",
        )

        # Verify the result
        assert draft_id == "existing-draft-id"
        assert is_new is False

        # Verify upsert was called with correct parameters
        mock_repo.draft_campaigns.upsert.assert_called_once_with(
            "requirements", sample_draft_data, "test-conversation"
        )
