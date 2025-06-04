For the issue: [#71](https://github.com/global-agent-hackathon/global-agent-hackathon-may-2025/issues/71)

RhythmWeaver - AI Generative Chords Improvisation, is a project that leverages Large Language Models (LLMs) to generate improvised musical chords in a textual format by applying their sequential data processing capabilities to the music. This system run by taking a URL of a webpage containing textual chords and lyrics using an agent framework (Agno) and a scraping tool (Firecrawl) to extract the content. This data is then analyzed by an LLMs (utilizing Groq for inference) to generate new "improvised" chords sequences based on the original chords and lyrics.

## Prerequisites

- Python 3.12 or higher
- Groq API Key
- Firecrawl API Key

## Setup Instructions

### 1. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Export your Agno Api Key:
```bash
# Windows
setx AGNO_API_KEY [YOUR_AGNO_API_KEY]

# Linux/Mac
export AGNO_API_KEY=[YOUR_AGNO_API_KEY]
```

### 5. Run the App

1. Start the Streamlit local server:
```bash
streamlit run rhythm_weaver.py
```
This will open browser at `http://localhost:8501`

2. In the app interface:
    - Enter your Groq and Firecrawl API keys.
    - Enter the chords web URL you want to improvise.
    - Click "Generate Improvisation".
    - Improvised chords and the lyrics displayed in HTML format.

## Features

- **Web scraping**: Web scraping and content extraction specific for textual chords and lyrics
- **Chords improvisation**: Using LLMs to improvise chords based on old chords and lyrics content

## Project Structure

```
rhythmweaver/
├── rhythm_weaver.py  # RhythmWeaver agent
├── requirements.txt  # Project dependencies
├── .env              # Environment variables
```