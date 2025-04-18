# VibeProto

VibeProto is a tool that helps non-coders build rapid prototypes (automation scripts, web apps, and utilities) using plain English prompts. The system uses OpenAI Codex CLI for code generation, the Agno framework for reasoning and memory, and a simple web UI for user input.

## Project Structure

- `frontend/`: Contains HTML, CSS, JavaScript files for the web UI
- `backend/`: Contains Python scripts (Agno agent and Flask server)
- `prototypes/`: Stores generated prototype files
- `agno/`: Contains the cloned Agno repo for reference

## Setup Instructions

### Prerequisites

- Node.js (v14 or later)
- Python (v3.8 or later)
- Git

### Node.js Setup

1. Install Node.js dependencies:
   ```
   npm install
   ```

### Python Setup

1. Activate the Python virtual environment:

   **Windows:**
   ```
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**
   ```
   source .venv/bin/activate
   ```

2. Install Python dependencies:
   ```
   pip install flask openai agno
   ```

### Environment Variables

Create a `.env` file in the root directory with the following content:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

1. Start the backend server:
   ```
   python backend/app.py
   ```

2. Start the frontend development server:
   ```
   npm start
   ```

3. Access the application at [http://localhost:3000](http://localhost:3000)

## Usage

1. Enter a plain English prompt describing what you want to build
2. Choose the type of prototype (automation script, web app, or utility)
3. Click "Generate Prototype"
4. View and test the generated prototype

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. 