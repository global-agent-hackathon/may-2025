# Talk2Find – Your Voice-Driven Knowledge Agent
## Global Agent Hackathon May 2025 Submission

## Project Title
Talk2Find – Your Voice-Driven Knowledge Agent

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
1. **Launch**: The user launches the program and clicks the "Start Recording" button on the Streamlit UI
2. **Voice Input**: When the user inputs speech, the system converts it to text in real-time
3. **Processing**: Multiple agents work together to understand the query and search for relevant information
4. **Results**: Relevant information such as PowerPoint slides is displayed in real time on the UI
5. **Interaction**: Clicking on the displayed content opens the corresponding file or URL

### Core Functionality
- **Speech-to-Text Conversion**: Real-time voice recognition and transcription
- **Multi-Agent Orchestration**: 
  - Query understanding and intent recognition agent
  - Information source selection agent
  - Search result ranking and optimization agent
- **Multi-Source Search**: Local files, web content, and private knowledge bases
- **Real-time Results**: Instant presentation of relevant information

### Multimodal Elements
- **Voice**: Primary input method for natural, hands-free interaction
- **Text**: Alternative input method for precise queries and accessibility
- **Visual**: Real-time display of search results, transcribed text, and interactive content

## Tools Used

### Key Libraries/Frameworks
- **Streamlit**: For creating the interactive web UI
- **Agno**: For LLM-based agent orchestration and coordination
- **Exa**: For fast, context-aware web search capabilities
- **Python Speech Recognition**: For voice-to-text conversion
- **Natural Language Processing**: For query understanding and intent extraction
- **File Processing Libraries**: For local document indexing and search

## UI Approach
The interface is designed for simplicity and real-time interaction:

- **Voice Recording Controls**: Start/stop recording buttons with visual feedback
- **Real-time Transcription Display**: Live text display of spoken queries
- **Search Results Panel**: Organized display of relevant information from multiple sources
- **Interactive Content**: Clickable results that open files or URLs
- **Source Indicators**: Clear labeling of information sources (local, web, private)

## Visuals
```
[Environmental Sensors] → [Data Collection Layer] → [AI Processing Engine]
                                                           ↓
[User Interface] ← [Response System] ← [Pattern Recognition & Learning]
```

## Team Information
- **Team Lead**: [@s-shohey](https://github.com/s-shohey)
- **Team Members**: 
  - [@nibura2002](https://github.com/nibura2002) 
  - [@jaewook-hwang-mcd](https://github.com/jaewook-hwang-mcd)
- **Background/Experience**: We are employees of [MC Digital, Inc.](https://www.mcdigital.jp/en/), with expertise in AI/ML, web development, and enterprise software solutions

## Technical Architecture

### System Components
1. **Voice Processing Pipeline**: 
   - Audio capture and preprocessing
   - Real-time speech-to-text conversion
   - Noise reduction and audio enhancement

2. **Agent Orchestration Layer** (Agno):
   - Query understanding and intent recognition
   - Information source selection and prioritization
   - Result ranking and relevance scoring

3. **Search Engine Integration**:
   - Local file indexing and search
   - Exa-powered web search
   - Private knowledge base connectors

4. **User Interface Layer** (Streamlit):
   - Real-time voice input handling
   - Dynamic result presentation
   - Interactive content navigation

### Key Features
- **Real-time Processing**: Instant voice recognition and search
- **Multi-source Integration**: Seamless access to diverse information sources
- **Context-aware Search**: Understanding of business context and user intent
- **Scalable Architecture**: Modular design for easy extension
- **Privacy-conscious**: Local processing where possible

## Installation and Setup

### Prerequisites
- Python 3.11+
- uv package manager
- Microphone access for voice input
- API keys for Agno and Exa services

### Quick Start
```bash
# Navigate to project directory
cd submissions/talk2find-voice-driven-knowledge-agent

# Install dependencies
uv sync --all-extras

# Setup environment variables
cp .env.sample .env
# Edit .env with your API keys

# Run the application
uv run streamlit run src/main.py
```

### Required Environment Variables
```bash
AGNO_API_KEY=your_agno_api_key_here
EXA_API_KEY=your_exa_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Prize Category
- ✅ **Best use of Agno**: Multi-agent orchestration for intelligent query processing
- ✅ **Best use of Exa**: Context-aware web search integration

## Demo Video Link
To be updated upon completion.

## Additional Notes

### Business Impact
This project addresses critical pain points in modern knowledge work:
- **Meeting Efficiency**: Instant access to relevant information during discussions
- **Document Discovery**: Quick retrieval from scattered file systems
- **Knowledge Sharing**: Easy access to organizational knowledge bases
- **Productivity Enhancement**: Reduced time spent searching for information

### Technical Innovation
- **Voice-first Design**: Natural interaction paradigm for busy professionals
- **Multi-agent Coordination**: Sophisticated AI orchestration for complex queries
- **Real-time Processing**: Immediate results without workflow interruption
- **Source Diversity**: Unified access to multiple information repositories

### Future Enhancements
- Integration with enterprise systems (SharePoint, Confluence, etc.)
- Advanced context understanding from meeting transcripts
- Collaborative features for team knowledge sharing
- Mobile application for on-the-go access

### Development Status
Currently in active development for the Global Agent Hackathon May 2025, with core functionality implemented and UI refinements in progress.

