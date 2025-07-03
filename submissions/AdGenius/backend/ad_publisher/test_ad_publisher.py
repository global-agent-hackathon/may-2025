import os
import unittest
from unittest import mock

from ad_publisher.ad_publisher import (
    BadRequestError,
    ForbiddenError,
    MissingApiKeyError,
    NotFoundError,
    ServerError,
    UnauthorizedError,
    create_ad,
    create_campaign,
)


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")


class TestAdPublisher(unittest.TestCase):
    @mock.patch.dict(os.environ, {"AD_PUBLISHER_API_KEY": "test_api_key"})
    @mock.patch("ad_publisher.ad_publisher.requests.post")
    def test_create_campaign_success(self, mock_post):
        # Setup
        mock_response = MockResponse({"campaign": {"id": "camp123", "name": "Test Campaign"}}, 201)
        mock_post.return_value = mock_response

        # Execute
        result = create_campaign(
            name="Test Campaign",
            startDate="2024-01-01",
            description="Test description",
            endDate="2024-12-31",
            status="draft",
            budget=1000.0,
        )

        # Assert
        self.assertEqual(result, {"campaign": {"id": "camp123", "name": "Test Campaign"}})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("Authorization", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_api_key")

        # Verify payload
        expected_payload = {
            "name": "Test Campaign",
            "startDate": "2024-01-01",
            "description": "Test description",
            "endDate": "2024-12-31",
            "status": "draft",
            "budget": "1000.0",  # Budget is converted to string in the API call
        }
        self.assertEqual(kwargs["json"], expected_payload)

    @mock.patch.dict(os.environ, {"AD_PUBLISHER_API_KEY": "test_api_key"})
    @mock.patch("ad_publisher.ad_publisher.requests.post")
    def test_create_ad_success(self, mock_post):
        # Setup
        mock_response = MockResponse({"ad": {"id": "ad456", "title": "Test Ad"}}, 201)
        mock_post.return_value = mock_response

        # Execute
        result = create_ad(
            title="Test Ad",
            targetUrl="https://example.com",
            description="Test ad description",
            imageUrl="https://example.com/image.jpg",
            status="active",
            campaignId="camp123",
        )

        # Assert
        self.assertEqual(result, {"ad": {"id": "ad456", "title": "Test Ad"}})
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        # Verify payload
        expected_payload = {
            "title": "Test Ad",
            "targetUrl": "https://example.com",
            "description": "Test ad description",
            "imageUrl": "https://example.com/image.jpg",
            "status": "active",
            "campaignId": "camp123",
        }
        self.assertEqual(kwargs["json"], expected_payload)

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        with self.assertRaises(MissingApiKeyError):
            create_campaign(name="Test", startDate="2024-01-01")

    @mock.patch.dict(os.environ, {"AD_PUBLISHER_API_KEY": "test_api_key"})
    @mock.patch("ad_publisher.ad_publisher.requests.post")
    def test_create_campaign_bad_request(self, mock_post):
        mock_response = MockResponse({}, 400)
        mock_post.return_value = mock_response

        with self.assertRaises(BadRequestError):
            create_campaign(name="Test", startDate="2024-01-01")

    @mock.patch.dict(os.environ, {"AD_PUBLISHER_API_KEY": "test_api_key"})
    @mock.patch("ad_publisher.ad_publisher.requests.post")
    def test_create_campaign_unauthorized(self, mock_post):
        mock_response = MockResponse({}, 401)
        mock_post.return_value = mock_response

        with self.assertRaises(UnauthorizedError):
            create_campaign(name="Test", startDate="2024-01-01")

    @mock.patch.dict(os.environ, {"AD_PUBLISHER_API_KEY": "test_api_key"})
    @mock.patch("ad_publisher.ad_publisher.requests.post")
    def test_create_ad_forbidden(self, mock_post):
        mock_response = MockResponse({}, 403)
        mock_post.return_value = mock_response

        with self.assertRaises(ForbiddenError):
            create_ad(
                title="Test Ad",
                targetUrl="https://example.com",
                campaignId="invalid_id",
            )

    @mock.patch.dict(os.environ, {"AD_PUBLISHER_API_KEY": "test_api_key"})
    @mock.patch("ad_publisher.ad_publisher.requests.post")
    def test_create_ad_not_found(self, mock_post):
        mock_response = MockResponse({}, 404)
        mock_post.return_value = mock_response

        with self.assertRaises(NotFoundError):
            create_ad(
                title="Test Ad",
                targetUrl="https://example.com",
                campaignId="nonexistent_id",
            )

    @mock.patch.dict(os.environ, {"AD_PUBLISHER_API_KEY": "test_api_key"})
    @mock.patch("ad_publisher.ad_publisher.requests.post")
    def test_create_campaign_server_error(self, mock_post):
        mock_response = MockResponse({}, 500)
        mock_post.return_value = mock_response

        with self.assertRaises(ServerError):
            create_campaign(name="Test", startDate="2024-01-01")


if __name__ == "__main__":
    unittest.main()