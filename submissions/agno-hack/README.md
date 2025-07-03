# AI Website Testing Agent Platform
[Demo](https://www.loom.com/share/072926be9dc347859a4cab17928bcbd2?sid=cb29978d-0a60-4327-ade2-ea2fb6b67cd6)


A powerful web-based platform for automated website testing that combines browser automation with AI analysis. This system features a **FastAPI backend** with **React frontend** providing real-time execution monitoring and comprehensive results visualization.

## 🎯 **System Architecture**

- **Backend**: FastAPI server with browser automation using Browser Use + Gemini 2.0 Flash
- **Frontend**: React web interface for test configuration and results visualization  
- **Agent Intelligence**: Custom controller actions for detailed reasoning capture
- **Real-time Monitoring**: Live status updates and execution progress tracking

## ✨ **Key Features**

- 🤖 **AI-Powered Agent Reasoning**: Real-time capture of agent thoughts and decision-making
- 🌐 **Web-Based Interface**: Beautiful, responsive frontend for test configuration
- 📸 **Intelligent Screenshot Capture**: Automated screenshot capture at key moments
- 📊 **Comprehensive Results**: Execution steps, screenshots, logs, and AI analysis
- 🔄 **Real-Time Updates**: Live status monitoring during test execution
- 📱 **Modern UI**: Gradient designs, color-coded insights, and intuitive navigation

## 🚀 **Quick Start**

### Prerequisites

1. **Python 3.8+** and **Node.js 16+** installed
2. **Google Gemini API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Chrome/Chromium browser** (for automation)

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd agno-hack
   ```

2. **Backend Setup**:
   ```bash
   # Install Python dependencies
   pip install agno browser-use langchain-google-genai python-dotenv fastapi uvicorn

   # Create environment file
   echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Platform

1. **Start the Backend API** (Terminal 1):
   ```bash
   python api_server.py
   ```
   ✅ Backend will start at: `http://localhost:8000`

2. **Start the Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm start
   ```
   ✅ Frontend will open at: `http://localhost:3000`

3. **Open your browser** and navigate to `http://localhost:3000`

## 🎮 **Using the Platform**

### 1. **Configure Your Test**
- **Target URL**: Enter the website you want to test
- **Task Description**: Describe what the agent should do (e.g., "Search for products and add to cart")
- **Screenshot Instructions**: Add specific screenshot requirements (optional)

### 2. **Execute Test**
- Click **"Execute Test"** to start automation
- Watch real-time status updates and progress
- Monitor agent reasoning and decision-making

### 3. **View Results**
- **🧠 Agent Thoughts**: See the AI's internal reasoning process with color-coded actions
- **📸 Screenshot Gallery**: View all captured screenshots with click-to-expand
- **🔄 Execution Steps**: Detailed timeline of actions and results
- **💬 AI Conversation**: Complete conversation log
- **📄 Log Files**: Access to detailed execution logs

### 4. **Analyze Results**
- Click **"Analyze Results"** for AI-powered analysis
- Get recommendations and compliance reports
- Export results for documentation

## 🖥️ **Frontend Features**

### **Agent Thoughts & Reasoning Display** 🧠
Beautiful gradient section showing real-time agent thoughts:
- ⚡ **Actions**: What the agent is doing
- 👁️ **Observations**: What the agent sees
- 🧭 **Decisions**: Agent's reasoning process
- 💭 **Info**: Additional insights

### **Results Dashboard** 📊
- **Summary Cards**: Success status, steps count, screenshots count
- **Interactive Screenshots**: Click-to-view gallery with step details
- **Execution Timeline**: Chronological view of all actions
- **Status Monitoring**: Real-time updates during execution

## 🔧 **API Endpoints**

The FastAPI backend provides these endpoints:

- `POST /execute-test` - Start a new test execution
- `GET /task-status/{task_id}` - Get execution status
- `GET /task-results/{task_id}` - Get execution results
- `GET /agent-thoughts/{task_id}` - Get agent reasoning log
- `POST /analyze-results/{task_id}` - Run AI analysis
- `GET /screenshots/{filename}` - Serve screenshot files
- `GET /health` - Health check

## 📁 **Generated Files**

The platform creates organized output in `operation_logs/`:

```
operation_logs/
├── screenshots/                    # All captured screenshots
├── detailed_agent_log_[task].txt   # Comprehensive execution log  
├── agent_thoughts_[task].txt       # Agent reasoning & decisions
├── agent_stdout_[task].txt         # Agent output capture
├── browser_execution_[task].json   # Detailed execution results
└── review_report_[task].json       # AI analysis report
```

## 💡 **Example Usage**

### **E-commerce Testing**:
```json
{
  "target_url": "https://shop.example.com",
  "task_description": "Search for 'wireless headphones', view the first product, and add it to cart",
  "screenshot_instructions": [
    {
      "step_description": "Screenshot of search results page",
      "filename": "search_results.png"
    },
    {
      "step_description": "Screenshot of product page",
      "filename": "product_page.png"
    },
    {
      "step_description": "Screenshot of cart after adding item",
      "filename": "cart_confirmation.png"
    }
  ]
}
```

### **Form Testing**:
```json
{
  "target_url": "https://forms.example.com/contact",
  "task_description": "Fill out the contact form with test data and submit",
  "screenshot_instructions": [
    {
      "step_description": "Empty form before filling",
      "filename": "empty_form.png"
    },
    {
      "step_description": "Completed form before submission",
      "filename": "filled_form.png"
    }
  ]
}
```

## 🛠️ **Customization**

### **Browser Configuration**
Modify browser settings in `api_server.py`:
```python
browser_config = BrowserConfig(
    headless=False,  # Set to True for headless mode
    disable_security=True,
    keep_alive=True,
    extra_browser_args=[
        "--disable-blink-features=AutomationControlled",
        "--window-size=1920,1080"
    ]
)
```

### **Agent Instructions**
The agent receives detailed instructions including:
- Navigation objectives
- Custom logging functions (`log_action`, `log_observation`, `log_decision`)
- Screenshot capture capabilities (`take_screenshot_now`)

## 🐛 **Troubleshooting**

### **Common Issues**:

1. **Backend won't start**:
   ```bash
   # Check if port 8000 is available
   lsof -i :8000
   # Kill any existing process
   kill -9 [PID]
   ```

2. **Frontend connection errors**:
   - Ensure backend is running on `http://localhost:8000`
   - Check browser console for CORS errors
   - Verify API endpoints are accessible

3. **No screenshots captured**:
   - Browser automation may be blocked by the website
   - Try setting `headless=False` for debugging
   - Check browser console for errors

4. **Agent thoughts not displaying**:
   - Check if `agent_thoughts_[task_id].txt` file is created
   - Verify `/agent-thoughts/{task_id}` endpoint is accessible
   - Look for errors in browser console

### **Debug Mode**:
- Set `headless=False` in browser config to watch execution
- Check `operation_logs/` for detailed error messages
- Use browser developer tools to inspect API calls

## 🔒 **Security Notes**

- Store API keys securely in `.env` file
- Frontend runs on localhost - configure CORS for production
- Screenshots may contain sensitive data - handle appropriately
- Browser automation detection is disabled for testing

## 📈 **System Requirements**

- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher  
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 1GB for logs and screenshots
- **Browser**: Chrome/Chromium for automation

## 🤝 **Support**

For issues:
1. Check the troubleshooting section above
2. Review log files in `operation_logs/`
3. Ensure all dependencies are installed correctly
4. Verify your `.env` file has a valid Gemini API key

---

**🎉 Enjoy automated website testing with AI-powered insights!**

This platform combines the power of modern web development with advanced AI to create an intuitive, comprehensive testing solution.
