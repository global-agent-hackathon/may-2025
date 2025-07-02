<h1 align='center'> ✨ Around the World with Agents ✨ </h1>
<h3 align='center'> An autonomous multi-agent travel planning system that creates personalized itineraries.</h3>

<p align="center">
<img src="https://github.com/user-attachments/assets/edd4c308-787e-4dae-a582-841c693bcb4b"/, height=700, width=650>
</p>

## Project Title
Collaborative Multi-Agent Travel Itinerary Planner

## Project Overview
It is an autonomous travel planning application that leverages multiple specialized independent agents to create comprehensive, personalized travel itineraries. The system employs a coordinated team of expert agents, each responsible for different aspects of travel planning including transportation, accommodation, sightseeing, and location determination.

## Project Goal
We wanted to create a lightweight application that users can use to get a personalized itinerary for their travel. The application aims to create a robust collaborative environment where multiple agents (with specific purposes) work towards the aim of generating the detailed itinerary. We have deliberately not included any high end tools or applications to reduce latency and response time.

### Demo Video
[Link](https://youtu.be/tsAbE_UCB9I)

## System Architecture

### Multi-Agent Components

**Transport Agent**
- Finds optimal transportation options between locations
- Integrates with Google Maps API for real-time data
- Provides cost and time estimates for car, train, and flight options

**Hotel Booking Agent**
- Recommends accommodations across budget categories
- Covers budget, mid-range, and luxury options
- Provides location-specific pricing and amenities

**Sightseeing Agent**
- Discovers top attractions and experiences
- Includes visit duration, timing recommendations, and travel fare
- Uses Google Maps API for extracting information

**Location Agent**
- Selects optimal next destinations based on remaining travel time and budget
- Considers distance, connectivity, and tourist appeal
- Maintains memory of visited locations

**Co-ordination Agent**
- A LLM is used to compile all the information into a detailed itinerary
- It finds the best combination of hotels, transport, etc. to keep the cost within the specified budget
- Finally, the detailed itinerary is presented to the user

### User Flow

1. Users input trip details including locations, budget, duration, and group size
2. The system coordinates specialized agents for each day of travel in the specific order : transport -> hotel booking -> sightseeing -> next location
3. Agents collaborate to plan transportation, accommodation, and activities
4. The coordination agent compiles information into a comprehensive itinerary maintaining the budget amount
5. Final output includes budget optimization and detailed recommendations

### Core Functionality
- **Agno**: Primary agent coordination and management
- **OpenAI GPT-4o-mini**: Primary language model for intelligent agents
- **Groq Llama 3.3-70b**: Fallback model for enhanced reliability
- **Model Context Protocol (MCP)**: External API integration
- **Google Maps API**: Location data, transportation and accomodation information
- **Streamlit**: Web application interface

<p align="center">
<img src="https://github.com/user-attachments/assets/f647a00b-36c7-4476-8f05-5d40561f3ad7"/>
</p>

<p align="center">
<img src="https://github.com/user-attachments/assets/a4b1675f-8690-4e28-bac8-08bd77416448"/>
</p>

<p align="center">
<img src="https://github.com/user-attachments/assets/0852b791-d233-4754-8009-b14f9e126d99"/>
</p>

### Architecture Pattern
```
User Input → Pipeline Orchestrator → Daily Agent Coordination → Final Itinerary

Each Day:
├── Transport Agent (route options)
├── Hotel Agent (accommodations)
├── Sightseeing Agent (attractions)
└── Location Agent (next destination)
```

## Tools Used
- **Agno**: Agentic framework
- **LLMs**: OpenAI, LLama3
- **MCP**: Google Maps API
- **Streamlit**: Web Interface

## User Interface
The application features a simplistic, functional interface built with Streamlit. The sidebar handles API configuration and trip parameters, while the main interface displays real-time progress and generates comprehensive itineraries. The design prioritizes clarity and usability over visual complexity.

## Installation and Setup

### Prerequisites
- Python 3.8+
- Node.js
- API keys for OpenAI, Groq, and Google Maps

### Installation Steps
```bash
git clone https://github.com/ArionDas/global-agent-hackathon-may-2025.git
cd submissions/around-the-world-with-agents/backend/
pip install -r requirements.txt
```

### Configuration
Create a `.env` file with required API keys (optional):
```
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### Running the Application
```bash
streamlit run pipeline.py
```

## Team Information

### Team Lead
- **GitHub**: @ArionDas
- **Role**: System Architecture & Agent Coordination
- **Focus**: Multi-agent systems, API integration, Python development

### Team Member
- **GitHub**: @Sahil0015
- **Role**: Agent Development & Travel Domain Logic
- **Focus**: Travel industry knowledge, agent specialization, user experience

### Team Background
We are a couple of undergrad students. We are actively working with Generative AI and Agentic AI concepts. <br> 
We stay active with the NLP research community as well. One of our papers recently went through NAACL! <br>
Happy to be a part of the hackathon! <br>
Cheers!
