# TubeWarden

Intelligent agent built with [Agno](https://docs.agno.com/introduction) and FastAPI to analyze YouTube videos and evaluate multiple categories such as reliability, manipulation, or accuracy. The results are sent via WebSocket to a browser extension or connected client.

---

## 🚀 Features

- Receive actions via REST API
- Intelligent video analysis using Agno
- Evaluation by configurable categories
- Send results via WebSocket to all connected clients
- Google Chrome extension to configure categories, send videos, and alter feed thumbnails

---

## 🧱 Project Structure

```
backend/
├── main.py              # FastAPI entry point
├── config.py            # Central configuration
├── agent/               # Agno agent and tools
├── api/                 # REST endpoints
├── queue/               # Async worker and queue
├── schemas/             # Pydantic models
├── ws/                  # WebSocket connection
chrome-extension/
├── manifest.json         # Main Chrome extension configuration
├── README.md             # Extension-specific documentation
├── public/               # Static assets for the popup UI
├── src/
│   ├── js/
│   │   ├── background.js # Background script: config, messaging, logging
│   │   └── content.js    # Content script: injects logic into YouTube pages
│   ├── css/
│   │   └── styles.css    # Styles injected into YouTube (badges, popups, etc.)
│   └── images/
│       └── icon.png      # Extension icon
```

---

## ⚙️ Requirements

- Python 3.9+
- [Poetry](https://python-poetry.org/)

---

## 📦 Installation

Clone the project:

```bash
# Initialize environment
poetry install

# Activate virtual environment
poetry shell
```

Install the Chrome extension:

1. Go to: chrome://extensions/
2. Click the "Load unpacked" button
3. Select the entire "chrome-extension" folder
4. The extension will appear in the current window and can be accessed later in the top right corner.
---

## 🧪 Development Mode

Start the server with auto-reload:

Directly with Python:

```bash
python -m backend.main
```

With Poetry

```bash
poetry run python -m backend.main
```

---

## 🌐 Endpoints

REST application running at: http://localhost:3000

### REST (input)

```http
POST /api/videos/evaluate
Content-Type: application/json

{
  "videoId": "abc123",
  "categories": ["hatred", "misinformation", "violence"],
  "customPrompts": {}
}
```

### WebSocket (output)

Connect to:

```
ws://localhost:3000/ws
```

You will receive `VideoScoreResult` objects like:

```json
{
  "type": "videoScore",
  "videoId": "abc123",
  "score": 8.5,
  "categories": {
    // Categories sent by the extension
    "hatred": 8.4,
    "misinformation": 10,
    "violence": 1.5
  },
  "evaluation_summary": "A detailed summary of the reasons for each category",
  "content_summary": "A brief overview of the video content, focusing on the main themes and messages",
}
```

---

## 📘 Interactive Documentation

Once the server is running, visit:

```
http://localhost:3000/docs
```

---