# 🧠 KnowledgeAgent

AI-Powered Content Analysis and Summarization Tool built with Agno Framework and Streamlit.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- uv (for package management)
- OpenAI-compatible API key

### Installation

1. Clone the repository and navigate to the project directory:
```bash
cd knowledge-agent
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Run the application:
```bash
uv run streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## 🔧 Configuration

1. Enter your API key in the sidebar
2. (Optional) Configure a custom base URL for OpenAI-compatible endpoints
3. Click "Save Configuration" to verify your connection

## 📝 Usage

1. **Input Text**: Paste the text you want to analyze
2. **Select Analysis Type**: Choose from various analysis options:
   - Executive Summary
   - Detailed Analysis
   - Concept Map
   - Key Points Extraction
   - SWOT Analysis
3. **Customize Options**: Adjust output length and preferences
4. **Analyze**: Click "Analyze Content" to process your text
5. **Download Results**: Save your analysis as a markdown file

## 🛠️ Development

### Project Structure
```
knowledge-agent/
├── app.py              # Main Streamlit application
├── pyproject.toml      # Project dependencies
├── README.md          # This file
└── agents.py           # AI Agents 
```

## 📄 License

MIT License

