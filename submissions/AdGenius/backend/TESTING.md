# Testing Framework for AdGenius Backend

This document outlines the testing framework for the AdGenius backend, including how to write and run tests.

## Overview

The testing framework is built on top of pytest and provides utilities to make writing and running tests easier. It includes:

- Test runners with various options
- Test templates and generators
- Helper functions for common test operations
- Test markers for organizing tests

## Running Tests

Use the `run_tests.py` script to run tests with various options:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run only API tests
python run_tests.py --api

# Run tests with coverage report
python run_tests.py --cov

# Run tests in parallel
python run_tests.py --parallel

# Run tests in watch mode (rerun on file changes)
python run_tests.py --watch

# Run tests with verbose output
python run_tests.py --verbose

# Run specific test files or directories
python run_tests.py chat_assistant/endpoints/tests/test_conversations.py
```

You can combine options:

```bash
# Run unit tests with coverage
python run_tests.py --unit --cov

# Run API tests in watch mode
python run_tests.py --api --watch
```

## Creating New Tests

Use the `create_test.py` script to generate new test files from templates:

```bash
# Create an API test
python create_test.py --type api --module user_management --class User

# Create a unit test
python create_test.py --type unit --module auth --class Authentication

# Create an integration test
python create_test.py --type integration --module database --class Repository

# Specify a custom directory for the test file
python create_test.py --type api --module chat --class Messages --dir chat_assistant/endpoints/tests
```

## Test Types and Markers

Tests are organized using markers:

- `@pytest.mark.unit`: Unit tests that test individual components in isolation
- `@pytest.mark.integration`: Integration tests that test components working together
- `@pytest.mark.api`: API tests that test the REST API endpoints
- `@pytest.mark.slow`: Tests that take a long time to run

## Helper Functions

The `utils/test_helpers.py` module provides helper functions for common test operations:

```python
from utils.test_helpers import assert_api_response, create_test_conversation

# Check API response status and content
data = assert_api_response(
    response,
    expected_status=200,
    expected_data={"success": True}
)

# Create a test conversation
conversation = create_test_conversation(client, "Test Conversation")
```

## Test Structure

Tests are organized in the following directory structure:

```
backend/
  ├── chat_assistant/
  │   ├── endpoints/
  │   │   └── tests/         # API tests for chat endpoints
  │   ├── repository/
  │   │   └── tests/         # Unit/integration tests for repository
  │   └── tests/             # General tests for chat_assistant
  ├── utils/
  │   ├── test_helpers.py    # Test helper functions
  │   └── test_templates.py  # Test templates
  ├── tests/                 # General backend tests
  ├── create_test.py         # Script to create new tests
  ├── run_tests.py           # Script to run tests
  └── pyproject.toml         # Test configuration
```

## Best Practices

1. **Test Organization**:
   - Use appropriate markers for tests
   - Group related tests in classes
   - Use descriptive test names

2. **Test Isolation**:
   - Tests should be independent of each other
   - Use fixtures to set up test data
   - Clean up after tests

3. **Test Coverage**:
   - Aim for high test coverage
   - Test happy paths and error cases
   - Test edge cases

4. **Test Maintenance**:
   - Keep tests up to date with code changes
   - Refactor tests as needed
   - Remove redundant tests 
