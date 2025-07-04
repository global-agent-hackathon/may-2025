# QA Test Generation System

This project is a comprehensive QA test generation system that uses AI to generate Gherkin scenarios and test scripts in various frameworks (Selenium, Playwright, Cypress, Behave) based on user requirements.

## Features

- **Gherkin Generator**: Create Gherkin feature files from user stories or requirements
- **Test Script Generator**: Generate test scripts in multiple frameworks:
  - Selenium (Java)
  - Playwright (TypeScript)
  - Cypress (JavaScript)
  - Behave (Python)
- **Chat Assistance**: Get help and explanations about testing concepts
- **File Upload**: Upload existing files to use as input for generation
- **Download**: Download generated feature files and test scripts

## Architecture

The system consists of two main components:

1. **Backend**: FastAPI-based Python backend that handles the AI generation logic
2. **Frontend**: React-based UI with a modern, user-friendly interface

## Setup and Installation

### Prerequisites

- Python 3.8+ for the backend
- Node.js 16+ for the frontend
- npm or yarn for package management

### Installation

1. Clone this repository
2. Run the setup script to install dependencies and start both services:

```bash
python setup_integration.py
```

This will:
- Install backend dependencies
- Install frontend dependencies
- Start the backend server on port 8000
- Start the frontend development server on port 5173

### Manual Setup

If you prefer to set up each component manually:

#### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Frontend Setup

```bash
cd gherkin-genai-dash-main
npm install
npm run dev
```

## Usage

1. Open your browser and navigate to http://localhost:5173
2. Log in with any username and role
3. Use the tabs to navigate between different generators:
   - Gherkin Generator: Create Gherkin feature files
   - Test Script Generator: Generate test scripts in various frameworks
   - Results Dashboard: View and manage generated tests
4. Enter your requirements or upload a file
5. Select the appropriate options and click Generate
6. Download the generated files as needed

## API Endpoints

The backend exposes the following API endpoints:

- `POST /generate`: Generate content based on text input
- `POST /generate-with-file`: Generate content using a file upload
- `GET /download/{filename}`: Download a generated file

## License

This project is licensed under the MIT License - see the LICENSE file for details.