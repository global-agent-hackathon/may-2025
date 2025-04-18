# VibeProto: Natural Language Prototyping for Non-Coders

## Overview

VibeProto is an innovative tool designed to empower non-coders to create web app prototypes and Python scripts using simple natural language prompts. By leveraging advanced AI technologies, VibeProto breaks down the barriers of traditional software development, making it accessible to anyone with an idea. Whether you're a designer sketching a web interface or an entrepreneur automating a task, VibeProto turns your words into working code, fast.

## Features

- **Web App Prototyping**: Generate functional HTML, CSS, and JavaScript prototypes from prompts like "Create a to-do list app."
- **Python Script Creation**: Produce Python scripts for automation or logic-based tasks with ease.
- **AI-Powered**: Utilizes OpenAI Codex for code generation and Agno for enhanced reasoning, prompt refinement and memory to store user preferneces.

## How It Works

VibeProto simplifies the coding process into a few intuitive steps:

1. **Input Your Idea**: Type a natural language prompt into the chat-like interface (e.g., "Build a calculator web app").
2. **Prompt Enhancement**: Refine and enhances your prompt with Agno for clearer, more specific results.
3. **Code Generation**: OpenAI Codex translates your prompt into functional code.
4. **Output**: View, run, or tweak the generated prototype or script directly.

The magic lies in the synergy of Codex's code-writing prowess and Agno's ability to understand and optimize user intent.

## Tools Used

- **OpenAI Codex**: Powers the generation of accurate and functional code.
- **Agno**: Enhances prompts and ensures outputs align with user expectations.
- *(Additional tools like Cursor or specific libraries can be added here based on your setup.)*

## Setup Instructions

Get VibeProto running on your machine with these beginner-friendly steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SukinShetty/VibeProto.git
   ```

2. **Navigate to the Project Folder**:
   ```bash
   cd VibeProto
   ```

3. **Install Dependencies**:
   - For the frontend (if applicable): `npm install`
   - For the backend (if applicable): `pip install -r requirements.txt`

4. **Set Up API Keys**:
   - Obtain an OpenAI API key and add it to a `.env` file as `OPENAI_API_KEY=your-key-here`.

5. **Run the Application**:
   - Start the frontend: `npm start` (runs on http://localhost:3000 by default).
   - Start the backend (if separate): `python app.py`.

## Usage

Once set up, using VibeProto is a breeze:

1. Open the app in your browser (e.g., http://localhost:3000).
2. Type a prompt in the chat interface (e.g., "Make a simple portfolio website").
3. (Optional) Click "Enhance" to refine your prompt with Agno.
4. Hit "Generate" to create your prototype or script.
5. Check the `prototypes/` folder for your generated code.
   - For web apps, open `index.html` in a browser.
   - For Python scripts, run them with `python script.py`.

**Tip for Non-Coders**: No coding knowledge? No problem! Just describe what you want, and VibeProto does the rest.

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