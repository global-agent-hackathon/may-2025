"""
Templates for creating new test files
"""

API_TEST_TEMPLATE = '''"""
API tests for {module_name}
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import httpx

from utils.test_helpers import assert_api_response, TestCase


@pytest.mark.api
class Test{class_name}API:
    """Test {class_name} API endpoints"""
    
    @pytest.mark.asyncio
    async def test_example(
        self,
        test_app: FastAPI,
        client: TestClient,
        override_dependencies
    ):
        """Example test case"""
        # Send a request
        response = client.get("/your-endpoint")
        
        # Validate response
        assert_api_response(
            response,
            expected_status=200,
            expected_data={"key": "expected_value"}
        )
'''

UNIT_TEST_TEMPLATE = '''"""
Unit tests for {module_name}
"""

import pytest
from unittest.mock import MagicMock, patch

from utils.test_helpers import TestCase


@pytest.mark.unit
class Test{class_name}:
    """Test {class_name} functionality"""
    
    def test_example(self):
        """Example test case"""
        # Arrange - setup your test
        value = "test"
        
        # Act - execute the functionality
        result = value.upper()
        
        # Assert - check the results
        assert result == "TEST"
    
    @pytest.mark.asyncio
    async def test_async_example(self):
        """Example async test case"""
        # Arrange
        expected = "value"
        
        # Act - with async/await
        actual = expected
        
        # Assert
        assert actual == expected
'''

INTEGRATION_TEST_TEMPLATE = '''"""
Integration tests for {module_name}
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from utils.test_helpers import TestCase


@pytest.mark.integration
class Test{class_name}Integration:
    """Test {class_name} integration with dependencies"""
    
    @pytest.mark.asyncio
    async def test_database_integration(self, db_session: AsyncSession):
        """Example database integration test"""
        # Perform database operations
        result = await db_session.execute("SELECT 1")
        value = result.scalar()
        
        # Verify results
        assert value == 1
'''

def get_template(template_type: str, module_name: str, class_name: str) -> str:
    """
    Get a template for a new test file
    
    Args:
        template_type: Type of test (api, unit, integration)
        module_name: Name of the module being tested
        class_name: Name of the class being tested
    
    Returns:
        Test file template as a string
    """
    templates = {
        "api": API_TEST_TEMPLATE,
        "unit": UNIT_TEST_TEMPLATE,
        "integration": INTEGRATION_TEST_TEMPLATE
    }
    
    template = templates.get(template_type.lower())
    if not template:
        raise ValueError(f"Unknown template type: {template_type}")
    
    return template.format(module_name=module_name, class_name=class_name) 