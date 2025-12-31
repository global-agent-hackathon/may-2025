<h1 align='center'>⚖️ Legalia.AI </h1>
<h3 align='center'> An AI-powered court case simulation with multiple roles and perspectives.</h3>

<p align="center">
  <img src="https://github.com/Sahil0015/global-agent-hackathon-may-2025/blob/main/submissions/Legalia.AI/legalia.ai_flowchart.png?raw=true" alt="Legalia Flowchart" width="650" height="700">
</p>

## Project Title
- Legalia.AI (AI Courtroom: Multi-Agent Justice Simulator)
- Pronunciation: lee-GAE-lee-uh dot A-I

## Project Overview
Our project presents a dynamic, interactive courtroom simulation powered entirely by multi-agent AI. Each character in the courtroom—judge, lawyers, victim, accused, witnesses, media, government officials, lab experts, and the public—is represented by a purpose-built AI agent with distinct roles, objectives, and reasoning capabilities.

Users can observe the court proceedings as they unfold autonomously, offering a realistic and immersive legal experience. This platform serves as an invaluable educational tool for aspiring law students and anyone interested in understanding courtroom dynamics.

Experience the future of legal education with our revolutionary Interactive Courtroom Simulation Platform—a cutting-edge ecosystem where artificial intelligence brings the intricacies of judicial proceedings to life.

## Project Objective
- It can be used as a simulator where user can sit back and enjoy reading the court case hearning.
- Used as a educational tool for law students.
- Can demonstrate real power of LLM Models and if they are capable of solving real-case on their own.
- If scaled correctly, it can use to get AI understanding on different pending and complete cases.

### 🎥 Demo Video
- 🔗 [Working demo of the website](https://www.youtube.com/watch?v=6Jd6F6EwKFs)  
- 🔗 [Flowchart walkthrough and details](https://www.youtube.com/watch?v=-QfZF2I7PaA)

### Website Link
Deployed on streamlit cloud - [Link](https://legalia-ai.streamlit.app/) 

## System Architecture

### Multi-Agent Components
**Judge Agent**
- Presides over court proceedings with impartial legal judgment  
- Applies laws and precedents to make fair rulings  
- Provides reasoned decisions

**Prosecutor Agent**
- Presents the case against the accused on behalf of the state  
- Uses evidence and witness testimony to prove guilt  
- Delivers concise, assertive arguments

**Plaintiff Agent**
- Represents the individual seeking justice or compensation  
- Shares personal impact and factual account of the harm suffered  
- Supports the prosecutions  

**Defense Agent**
- Defends the accused and challenges prosecution claims  
- Raises reasonable doubt and advocates for acquittal or leniency  
- Strategically responds with rebuttals

**Accused Agent**
- Provides the defendant’s perspective and testimony  
- Maintains consistency and honesty while defending innocence or expressing remorse  
- Keeps responses authentic

**Witness Agent**
- Delivers factual testimony based on firsthand knowledge  
- Responds to direct and cross-examination professionally  
- Maintains composure and clarity

**Expert Agent**
- Analyzes and interprets forensic or technical evidence  
- Explains complex findings in accessible terms  
- Provides objective expert opinions 

**Media & Public Agent**
- Reports public reaction and community sentiment  
- Presents concise courtroom updates in a journalistic tone  
- Maintains objectivity and ethics

**Narrative Agent**
- Compiles comprehensive, chronological case summaries  
- Connects testimonies, evidence, and events into a coherent storyline  
- Produces structured legal documentation

### User Flow
1. Users input their OpenAI API key to begin. A sample case is provided to start with a trial demo.
2. The system activates specialized agents for each role—such as judge, lawyers, witnesses, etc.—based on the day’s schedule.
3. These agents autonomously collaborate to simulate the courtroom hearing.
4. A coordination agent compiles all interactions into a structured summary, preserving logical flow and context.
5. The final output includes:
   - A simulated courtroom trial
   - Generated public/media opinion
   - A detailed narrative report of the case

### Core Functionality
- **Agno**: Manages multi-agent orchestration and role-based coordination  
- **OpenAI GPT-4o-mini**: Powers all intelligent agents for natural language interaction  
- **DuckDuckGo & Reasoning Tools**: Enhance agent responses with external facts and structured logic  
- **Streamlit**: Provides a user-friendly web interface for interactive simulation

### Architecture Pattern
```
User Input → Agent Orchestrator → Daily Court Proceedings → Final Case Summary

Each Day:
├── Judge Agent (presides and makes rulings)
├── Prosecutor & Plaintiff Agents (present charges and claims)
├── Defense & Accused Agents (defend and testify)
├── Witness & Expert Agents (provide evidence and insights)
└── Media/Public Agent (report public reaction)

Final Output:
├── Narrative Agent (compiles detailed case summary)
└── Streamlit Interface (displays interactive simulation)
```

## Tools Used
- **Agno**: Agentic framework
- **LLMs**: OpenAI
- **Streamlit**: Web Interface

## User Interface
The application features a simplistic, functional interface built with Streamlit. The sidebar handles all necessary inputs to be written, while the main interface displays real-time progress and generates comprehensive hearings. The design prioritizes clarity, usability and visual complexity.

## Installation and Setup

### Prerequisites
- Python 3.8+
- Agno and Streamlit framework knowledge
- API key for OpenAI

### Installation Steps
```bash
git clone https://github.com/Sahil0015/global-agent-hackathon-may-2025.git
cd submissions/Legalia.AI/backend
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app.py
```

## Team Information

### Team Lead
- **GitHub**: @Sahil0015
- **Role**: System Architecture & Agent Coordination
- **Focus**: Multi-agent systems, API integration, Python development

### Team Member
- **GitHub**: @ArionDas
- **Role**: Project setup, Deployment and Agents
- **Focus**: User experience and working of the app

### Team Background
We are undergrad students from IIIT Ranchi. We are actively working with Generative AI and Agentic AI concepts. <br> 
Happy to be a part of the hackathon! <br>
