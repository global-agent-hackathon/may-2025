# Talk2Find – Your Voice-Driven Knowledge Agent

## Overview of the Idea

Have you ever found yourself flustered during an important business meeting when unfamiliar terms are mentioned? Have you ever spent 30 minutes trying to find a single slide from dozens of scattered PowerPoint files?

This agent is designed to solve such problems in real-time. When a user inputs voice or text queries, the system searches for the most relevant information sources and presents them immediately.

## Project Goal

The goal of this project is to build a multimodal search agent system that can present relevant information in real time, in response to vague and context-dependent user inquiries.

By utilizing Agno for LLM-based agent orchestration, the system interprets search intent from voice or text inputs and selects the most appropriate information source (e.g., local files, internal knowledge bases, or the web).

Additionally, by incorporating Exa, the system performs fast, context-aware web searches, and integrates the results into a unified UI.

Through the development of a practical prototype, we aim to validate how the combination of agent technologies and multimodal interfaces can address real-world business challenges.

## How It Works

### User Flow
1. The user launches the program and clicks the "Start Recording" button on the Streamlit UI
2. When the user inputs speech, relevant information such as PowerPoint slides is displayed in real time on the UI
3. Text input is also supported
4. The information may include:
   - Locally stored files (e.g., PDFs)
   - Text retrieved from the internet
   - Content from private sources like Confluence
5. Clicking on the displayed content opens the corresponding file or URL

### Core Functionality
- Converts speech input into text
- Multiple agents work together:
  - One generates summaries and search queries
  - Another selects information sources
  - Another adjusts the ranking of search results

### Multimodal Elements
- **Voice**: Primary input method for natural interaction
- **Text**: Alternative input method for precise queries
- **Visual**: Real-time display of search results and content

## Tools Used

### Key Libraries/Frameworks
- **Streamlit**: For web UI
- **Agno**: For agent orchestration
- **Exa**: For web search
- **Python**: Core development language
- **Speech Recognition**: For voice-to-text conversion
- **Natural Language Processing**: For query understanding

## UI Approach

The interface includes:
- A display area for real-time transcribed text from audio input
- A section to show search results
- Interactive elements for opening files and URLs
- Voice recording controls

## Visuals

Work in progress - developing intuitive interface for voice-driven search experience.

## Team Information

- **Team Lead**: [@s-shohey](https://github.com/s-shohey) - Project Lead & AI Engineer
- **Team Members**: 
  - [@nibura2002](https://github.com/nibura2002) - Backend Developer
  - [@jaewook-hwang-mcd](https://github.com/jaewook-hwang-mcd) - Frontend Developer
- **Background/Experience**: We are employees of [MC Digital, Inc.](https://www.mcdigital.jp/en/)

## Technical Architecture

### Core Components
1. **Voice Processing Pipeline**: Speech-to-text conversion and audio handling
2. **Agent Orchestration**: Agno-powered multi-agent system
3. **Search Engine**: Exa integration for web search capabilities
4. **Local File Indexing**: System for searching local documents
5. **UI Layer**: Streamlit-based interactive interface

### Key Features
- Real-time voice recognition
- Multi-source information retrieval
- Context-aware search ranking
- Unified result presentation
- Cross-platform compatibility

## Installation and Setup

### Prerequisites
- Python 3.11+
- uv package manager
- Microphone access for voice input

### Quick Start
```bash
# Clone and setup
cd submissions/talk2find-voice-driven-knowledge-agent

# Install dependencies
uv sync --all-extras

# Setup environment variables
cp .env.sample .env
# Edit .env with your API keys (Agno, Exa, etc.)

# Run the application
uv run streamlit run src/main.py
```

### Environment Variables
```bash
# Required API keys
AGNO_API_KEY=your_agno_api_key_here
EXA_API_KEY=your_exa_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Demo Video Link
To be updated upon completion.

## Additional Notes

This project addresses real-world business challenges by providing instant access to relevant information through natural voice interaction. The system is designed to be particularly useful in:

- Business meetings and presentations
- Research and knowledge discovery
- Document management and retrieval
- Real-time information lookup

The combination of voice input, AI-powered search, and multi-source information retrieval creates a powerful tool for knowledge workers who need quick access to scattered information sources.

## Prize Category
- Best use of Agno
- Best use of Exa

## Development Status
Currently in active development for the Global Agent Hackathon May 2025.
