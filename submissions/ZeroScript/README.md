# ZeroScript - Automated Browser Testing Framework

ZeroScript is an automated browser testing framework that uses AI-powered agents to execute test cases. It combines the power of Google's Generative AI with browser automation to create intelligent test execution.

## Features

- 🤖 AI-powered test execution using Browser-Use and Google's Gemini model
- 🌐 Browser automation with recording and screenshot capabilities
- 📝 YAML-based test case definitions
- 📊 JSON test execution reports
- 📸 Automatic screenshot capture for test steps
- 🔄 Support for test hooks (beforeEach, afterEach)
- 🔒 Secure handling of sensitive data

## Project Structure

```
ZeroScript/
├── agent.py              # Core agent implementation
├── test_runner.py        # Test execution engine
├── views.py             # Data models
├── secrets.py           # Sensitive data configuration
├── requirements.txt     # Project dependencies
├── tests/              # Test case directory
│   └── *.yml          # YAML test files
└── data/              # Generated data
    ├── recordings/    # Browser recordings
    ├── conversations/ # AI conversation logs
    ├── screenshots/   # Test screenshots
    └── reports/      # Test execution reports
```

## Prerequisites

- Python 3.7 or higher
- Google Gemini API key

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
```

## Writing Test Cases

Test cases are defined in YAML files within the `tests` directory. Here's an example:

```yaml
hooks:
  beforeEach: |
    # Pre-test setup instructions
    Navigate to https://example.com
  afterEach: |
    # Post-test cleanup instructions
    Clear browser cookies

tests:
  - id: "login_test_001"
    name: "Valid Login Test"
    instructions: |
      # Test steps
      1. Enter username in username field
      2. Enter password in password field
      3. Click login button
      4. Verify dashboard is displayed
```

## Running Tests

Execute all tests:
```bash
python test_runner.py
```

## Test Reports

After test execution, reports are generated in the `data/reports` directory:
- JSON report with test results
- Screenshots of test execution steps
- Browser recordings (if enabled)

## Configuration

### Browser Configuration
Modify browser settings in `agent.py`:
```python
browser_config = BrowserConfig(
    headless=False,  # Set to True for headless execution
)
```

### Sensitive Data
Store sensitive data in `secrets.py`:
```python
sensitive_data = {
    'username': 'your_username',
    'password': 'your_password'
}
```

## Acknowledgments

- Google Gemini AI for the language model
- Browser-Use for browser automation using an AI Agent
