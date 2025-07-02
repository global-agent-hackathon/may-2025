# TubeWarden - Chrome Extension

This extension analyzes videos displayed on YouTube (main feed and subscriptions), sends their IDs to a local server for evaluation, and displays scores and performs actions based on server responses.

## Features

- **Video Analysis**: Detects and evaluates videos in the main feed and subscriptions page
- **Visual Scores**: Displays numerical scores in the upper right corner of each thumbnail
- **Automatic Actions**: Hides or marks videos based on their score
- **YouTube Integration**: Allows automatically using the "Not interested in this channel" function
- **Customizable Categories**: Configure which aspects to evaluate (manipulation, intellectual health, etc.)
- **Custom Prompts**: Define specific rules to filter videos
- **Action Log**: View a history of actions performed

## Installation

### Manual Installation (Developer Mode)

1. Download or clone this repository to your computer
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the upper right corner
4. Click "Load unpacked" and select the extension folder
5. The extension should appear in the list and be ready to use

## Configuration

### Required Server

This extension requires a local server that implements:

1. **REST API** to receive video IDs for evaluation
2. **WebSocket Server** to send evaluation results

### Extension Configuration

1. Click on the extension icon to open the configuration panel
2. Configure server URLs:
   - REST server URL (default: `http://localhost:3000`)
   - WebSocket URL (default: `ws://localhost:3000/ws`)
3. Select the evaluation categories you want to activate
4. Configure score thresholds for automatic actions
5. Add custom prompts if desired
6. Click "Save Configuration"

## Server Implementation

### Required Endpoints

#### REST API

- **POST /api/videos/evaluate**
  - Receives video IDs for evaluation
  - Example payload:
    ```json
    {
      "videoId": "dQw4w9WgXcQ",
      "categories": ["hatred", "misinformation", "violence"],
      "customPrompts": ["remove videos about Spain-Puerto Rico reunification"]
    }
    ```
  - Expected response:
    ```json
    {
      "success": true,
      "message": "Video added to evaluation queue"
    }
    ```

#### WebSocket

- The server must send WebSocket messages with the following format when it completes an evaluation:
  ```json
  {
    "type": "videoScore",
    "videoId": "dQw4w9WgXcQ",
    "score": 7.5,
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

## Project Structure

```
chrome-extension/
├── manifest.json               # Main extension configuration
├── src/
│   ├── js/
│   │   ├── background.js       # Background script
│   │   └── content.js          # Content script for YouTube
│   ├── css/
│   │   └── styles.css          # Styles for injected elements
│   └── images/                 # Extension icons
│       ├── icon.png
└── public/
    ├── popup.html              # Configuration popup HTML
    ├── popup.css               # Popup styles
    └── popup.js                # Popup JavaScript
```