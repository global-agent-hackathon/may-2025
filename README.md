# VibeProto: Natural Language Prototyping for Non-Coders

## Overview

VibeProto is an innovative tool designed to empower non-coders to create web app prototypes and Python scripts using simple natural language prompts. By leveraging advanced AI technologies, VibeProto breaks down the barriers of traditional software development, making it accessible to anyone with an idea. Whether you're a designer sketching a web interface or an entrepreneur automating a task, VibeProto turns your words into working code, fast.

## Features

- **Web App Prototyping**: Generate functional HTML, CSS, and JavaScript prototypes from prompts like "Create a to-do list app."
- **Python Script Creation**: Produce Python scripts for automation or logic-based tasks with ease.
- **AI-Powered**: Utilizes OpenAI's GPT-4 for code generation and Agno for enhanced reasoning and prompt refinement.
- **Session Management**: Save and manage your generated prototypes with an easy-to-use interface.
- **Prompt Enhancement**: AI-powered prompt refinement to get better results.
- **Detailed Instructions**: Step-by-step guides for using generated code, tailored for non-technical users.

## Setup Requirements

Before you begin, ensure you have:
- Python 3.8 or higher
- Node.js and npm (for frontend)
- OpenAI API key

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SukinShetty/VibeProto.git
   cd VibeProto
   ```

2. **Backend Setup**:
   ```bash
   # Create and activate a virtual environment (recommended)
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Create .env file and add your OpenAI API key
   echo "OPENAI_API_KEY=your-key-here" > .env
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

1. **Start the Backend Server**:
   ```bash
   # Make sure you're in the project root and virtual environment is activated
   python prototype_agent.py
   ```
   The backend will start on `http://localhost:5000`

2. **Start the Frontend**:
   ```bash
   # In a new terminal, navigate to the frontend directory
   cd frontend
   # Start the development server
   npm start
   ```
   The frontend will be available at `http://localhost:3000`

## Using VibeProto

1. **Create a New Session**:
   - Click "New Session" to start a fresh prototype.
   - Your sessions are automatically saved and can be accessed later.

2. **Generate Code**:
   - Choose the type (Web App or Python Script).
   - Type your idea in plain English.
   - (Optional) Click "Enhance Prompt" for better results.
   - Click "Generate Prototype".

3. **View and Use Generated Code**:
   - The generated code appears in the right panel.
   - Detailed instructions for using the code are provided below it.
   - Use the "Copy Code" or "Download" buttons to save your work.

4. **Managing Sessions**:
   - Your sessions are listed in the left sidebar.
   - Click on a session name to load it.
   - Use the "..." menu to rename or delete sessions.

## Example Prompts

For Web Apps:
- "Create a weather app that shows temperature and conditions for a city"
- "Build a todo list with add and delete functions"

For Python Scripts:
- "Write a script to rename files in a directory"
- "Create a data scraper for a website"

## Troubleshooting

If you encounter issues:

1. **Backend won't start**:
   - Check if Python virtual environment is activated
   - Verify OpenAI API key in `.env` file
   - Ensure port 5000 is not in use

2. **Frontend won't start**:
   - Check if Node.js is installed
   - Run `npm install` again
   - Ensure port 3000 is not in use

3. **Generation fails**:
   - Verify your OpenAI API key is valid
   - Check backend console for error messages

## Tools Used

- **OpenAI GPT-4**: Powers the generation of accurate and functional code
- **Flask**: Backend server framework
- **React**: Frontend framework
- **SQLite**: Session storage
- **Agno**: Enhanced reasoning and prompt refinement

## Demo Video

Watch the Demo Video *https://vimeo.com/1076698785?share=copy#t=0*

## Visuals
https://drive.google.com/file/d/1kVZ1R5oOqDegvw-QgHDLF-2ToxMFd1Yj/view?usp=sharing
User Flow DIagram: https://drive.google.com/file/d/17SEgnxu7maWrthKX9-ijAScVvYa10IfY/view?usp=sharing


## Team Information

- **Team Lead**: Sukin Shetty (GitHub: SukinShetty) - Developer and Creator
- **Team Members**: Solo project
- **Background**: Non-coder turned AI Buider. I am also an AI Educator. I built VibeProto to make software creation as intuitive as a conversation. Using tools like Codex and Agno, I'm passionate about bringing coding to everyone.I have been using AI to build AI Tech products since a year now.

## Future Plans
VibeProto is just the beginning! Planned enhancements include:
1. **Multimodal Inputs**: Support for sketches or images alongside text prompts. and voice enabled prompt generation.
2. **Expanded Languages**: Adding more frameworks and programming languages.
3. **Advanced Webapps Executions**: Will integrate more agents to build sophasticated webapps with simple plain english prompt.
4. **Share & Deployment**: Shareable links to the project created by user so that they can share to others and make delpoyment easy.
5. **Community Hub**: A marketplace for sharing and remixing prototypes. 