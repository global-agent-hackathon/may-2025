# PatientPal: Getting Started

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/global-agent-hackathon/global-agent-hackathon-may-2025
cd submissions/patientpal
```

2. Set up environment variables:
- Copy the `.env.example` file to `.env`
- Add your API keys for the required services:
  - GROQ_API_KEY
  - AGNO_API_KEY
  - MEM0_API_KEY
  - FIRECRAWL_API_KEY or EXA_API_KEY (optional)

3. Run the setup script:
```bash
chmod +x run.sh
./run.sh
```

This script will:
- Create a virtual environment
- Install required dependencies
- Launch the application

4. Access the application:
- Open your browser and go to http://localhost:7860

### Using Docker (Alternative)

1. Build the Docker image:
```bash
docker build -t patientpal .
```

2. Run the Docker container:
```bash
docker run -p 7860:7860 -v $(pwd)/data:/app/data patientpal
```

## Usage Guide

### Consultation Analysis
1. Upload an audio recording of your doctor's consultation, take a photo of your consultation notes, or type/paste your notes
2. Click "Process Consultation"
3. Review the summary and identified medical terms
4. Click on any highlighted medical term to see a plain-language explanation

### Medication Management
1. You can either:
   - Click the "Extract Medications to Management Tab" button after processing a consultation, or
   - Enter your medication details manually in the text box, one medication per line
2. Format: Name, dosage, frequency, and timing instructions
3. Click "Generate Schedule"
4. View your personalized medication schedule
5. Use the "Check Upcoming Reminders" button to see what medications are due

## Technology Stack
- **Gradio**: Web interface
- **Groq API**: LLM for summarization and term identification
- **Agno**: Workflow orchestration
- **Mem0**: Persistent memory for user data
- **Firecrawl/Exa**: Web search for RAG (medical term explanations)
- **Python Schedule**: Medication reminder scheduling
