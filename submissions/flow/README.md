# FLOW - Browser Extension

FLOW is an intelligent Chrome extension powered by Agno and Browser Use that supercharges your browsing experience with cutting-edge AI tools — empowering you to create, analyze, and learn faster than ever.

## 🧠 How it fits into your daily routine:
Whether you're reading articles, researching a topic, managing payments, or creating content, FLOW works quietly in the background to enhance every step. It’s like having a smart assistant right in your browser—helping you summarize long pages, generate ideas on the fly, create visual assets, and even manage communications or payments—all without switching tabs. From work to personal learning, FLOW makes your everyday browsing more productive, insightful, and effortless.

## Folder Structure
```
FLOW/
├── README.md                  # Project documentation and setup instructions
├── FRONTEND/                  # Frontend code for the Chrome extension
│   ├── images/                # Image assets & icons used in the extension
│   ├── package.json           # Node.js package configuration and dependencies
│   ├── package-lock.json      # Locked versions of npm dependencies
│   ├── eslint.config.js       # Additional ESLint configuration
│   ├── manifest.json          # Chrome extension manifest file
│   ├── LICENSE                # Project license file
│   ├── popup.html             # Main extension popup interface
│   ├── popup.css              # Styles for the popup interface
│   ├── popup.js               # Core popup functionality
│   ├── background.js          # Background service worker for extension
│   ├── contentScript.js       # Content script for font injection
│   ├── elementPicker.js       # Element selection and analysis functionality
│   ├── aiChatbot.js           # AI chatbot interface and functionality with Browser-use
│   ├── tab2.js                # Tab 2 functionality (Color Analysis)
│   ├── tab3.js                # Tab 3 functionality (Font & Vector)
│   ├── tab4.js                # Tab 4 functionality (Color Palette)
│   ├── tab5.js                # Tab 5 functionality (Payment Links)
│   ├── tab5.css               # Styles for Tab 5
│   ├── tab6.js                # Tab 6 functionality (Color Analysis)
│   ├── tab7.js                # Tab 7 functionality (Flashcard Generation)
│   ├── analyzeColors.js       # Color analysis functionality
│   ├── analyzeCurrentTab.js   # Current tab analysis functionality
│   ├── captureAndAnalyseFont.js # Font capture and analysis
│   ├── captureTabColors.js    # Color capture from current tab
│   ├── fetchAiResponse.js     # AI response fetching functionality
│   ├── fetchColorNames.js     # Color name fetching functionality
│   ├── generateVector.js      # Vector generation functionality
│   ├── imageToAgno.js         # Image to Agno conversion
│   ├── MarkdownToHTML.js      # Markdown to HTML conversion
│   ├── renderColorPalette.js  # Color palette rendering
│   ├── renderFontCards.js     # Font card rendering
│   ├── savedPalette.js        # Saved color palette functionality
│   └── updateColorPalette.js  # Color palette update functionality
└── BACKEND/                   # Backend server code
    ├── __pycache__/           # Python bytecode cache
    ├── main.py                # Main backend server file
    ├── analyze_toolkit.py     # Analysis toolkit functionality
    ├── browser_toolkit.py     # Browser-Use interaction toolkit
    ├── open_chrome.py         # Chrome browser control 
    ├── razorpay_toolkit.py    # Payment integration toolkit
    └── requirements.txt       # Python dependencies
```

## 🎯 Core Components

### 🤖 AI Agents

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
  <thead>
    <tr>
      <th>Agent Name</th>
      <th>Role</th>
      <th>Tools</th>
      <th>Key Features</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Visual Designer</td><td>Color theory &amp; composition expert</td><td>GPT-4</td><td>Color schemes, visual composition</td></tr>
    <tr><td>Typography Expert</td><td>Font &amp; layout specialist</td><td>GPT-4</td><td>Font selection, typography hierarchy</td></tr>
    <tr><td>UX Writer</td><td>Microcopy &amp; content guidance</td><td>GPT-4</td><td>UX content, user guidance</td></tr>
    <tr><td>Image Analysis Agent</td><td>Visual content analyzer</td><td>AnalyzeToolkit</td><td>Image insights, design inspiration</td></tr>
    <tr><td>Accessibility Expert</td><td>WCAG compliance specialist</td><td>GPT-4</td><td>Accessibility standards, contrast ratios</td></tr>
    <tr><td>Animation Specialist</td><td>Motion design expert</td><td>GPT-4</td><td>Transitions, micro-interactions</td></tr>
    <tr><td>Brand Strategist</td><td>Brand consistency manager</td><td>GPT-4</td><td>Brand guidelines, voice consistency</td></tr>
    <tr><td>Language Expert</td><td>Translation specialist</td><td>GPT-4</td><td>Multi-language translation</td></tr>
    <tr><td>Browser Automation Agent</td><td>Web automation expert</td><td>BrowserUseToolkit</td><td>Web scraping, form automation</td></tr>
    <tr><td>PaymentLinkGenerator</td><td>Payment link creator</td><td>RazorpayPaymentLink</td><td>Payment link generation</td></tr>
    <tr><td>PaymentEmailSender</td><td>Email notification handler</td><td>ResendTools</td><td>Payment link distribution</td></tr>
    <tr><td>FlashcardGenerator</td><td>Educational content creator</td><td>WebsiteTools</td><td>Flashcard generation</td></tr>
  </tbody>
</table>

### 👥 Teams

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
  <thead>
    <tr>
      <th>Team Name</th>
      <th>Mode</th>
      <th>Members</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>PaymentProcessingTeam</td><td>Coordinate</td><td>PaymentLinkGenerator, PaymentEmailSender</td><td>End-to-end payment processing</td></tr>
    <tr><td>Creative Design Team</td><td>Route</td><td>All design specialists</td><td>Comprehensive design solutions</td></tr>
  </tbody>
</table>

### 🔌 API Endpoints

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
  <thead>
    <tr>
      <th>Endpoint</th>
      <th>Method</th>
      <th>Purpose</th>
      <th>Key Inputs</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>/api/ai-response</td><td>POST</td><td>Design queries</td><td>prompt, image_url, element</td></tr>
    <tr><td>/api/browser/execute</td><td>POST</td><td>Browser automation</td><td>prompt</td></tr>
    <tr><td>/api/payments/generate-link</td><td>POST</td><td>Payment link generation</td><td>api_key, amount, customer details</td></tr>
    <tr><td>/api/send-payment-link</td><td>POST</td><td>Payment link distribution</td><td>Payment details, customer info</td></tr>
    <tr><td>/api/track-payments</td><td>POST</td><td>Payment monitoring</td><td>api_key, limit, status</td></tr>
    <tr><td>/api/analyze-images</td><td>POST</td><td>Image analysis</td><td>prompt</td></tr>
    <tr><td>/api/analyze-tab</td><td>POST</td><td>Tab analysis</td><td>prompt</td></tr>
    <tr><td>/api/translate</td><td>POST</td><td>Text translation</td><td>element, prompt</td></tr>
    <tr><td>/api/generate-flashcards</td><td>POST</td><td>Flashcard creation</td><td>url</td></tr>
  </tbody>
</table>

### 🛠️ Tools & Dependencies

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
  <thead>
    <tr>
      <th>Category</th>
      <th>Tools</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Core Framework</td><td>Flask, CORS</td><td>Backend, CORS handling</td></tr>
    <tr><td>Frontend Framework</td><td>HTML, CSS, JS</td><td>Extension framework</td></tr>
    <tr><td>Agentic Framework</td><td>Agno, Browser-use</td><td>AI and Automation</td></tr>
    <tr><td>AI Integration</td><td>OpenAI, GPT-4</td><td>AI model integration</td></tr>
    <tr><td>Search</td><td>DuckDuckGo</td><td>Search functionality</td></tr>
    <tr><td>Custom Toolkits</td><td>BrowserUseToolkit</td><td>Browser automation</td></tr>
    <tr><td></td><td>RazorpayPaymentLink</td><td>Payment processing</td></tr>
    <tr><td></td><td>RazorpayTrackerToolkit</td><td>Payment tracking</td></tr>
    <tr><td></td><td>AnalyzeToolkit</td><td>Content analysis</td></tr>
    <tr><td></td><td>WebsiteTools</td><td>Web content extraction</td></tr>
    <tr><td></td><td>ResendTools</td><td>Email functionality</td></tr>
  </tbody>
</table>



## Features

## 1. Context Menu Features
Right-click anywhere on a webpage to access powerful tools:

### 🔍 Analyze Element  
Easily inspect and understand any element on a webpage — powered by **Agno**.  

**How to use:**  
1. Right-click anywhere in Chrome.  
2. Go to **Flow → Analyze Element**.  
3. Your cursor will switch to the **Element Picker**.  
4. Click on any element — image, text, or paragraph — to get instant, AI-powered insights.

DEMO -

https://github.com/user-attachments/assets/29521d26-9efc-4d00-adbd-8a22bf6b704f




### 🌐 Translate Text  
Translate any text element on a webpage directly into your chosen language — seamlessly integrated into the page.

**Supported languages:**  
- Spanish 🇪🇸  
- French 🇫🇷  
- German 🇩🇪  
- Japanese 🇯🇵  
- Chinese 🇨🇳  
- Russian 🇷🇺  
- Arabic 🇸🇦  
- Hindi 🇮🇳

**How to use:**  
1. Right-click anywhere on a webpage in Chrome.  
2. Go to **Flow → Translate Text**, then select your target language.  
3. Your cursor will switch to the **Element Picker**.  
4. Click on any text element — a sentence, paragraph, or entire content block.  
5. The selected text will be instantly translated and **replaced in the page DOM**, right where it was.

*No popups. No distractions. Just seamless in-place translation.*

DEMO -

https://github.com/user-attachments/assets/66d2b000-e341-4523-811c-652f43da9a30




### 🤖 Flowy  
Meet your intelligent in-browser assistant — powered by **Browser Use**.  
**Flowy** is one of the most powerful tools for interacting with your current browser tab — no popups, no switching windows, no distractions.

**What Flowy can help you with:**  
- 🔍 Analyzing page content  
- 📧 Assisting with email writing  
- 📝 Helping fill out forms  
- 📊 Extracting data from web pages  
- 🧠 Summarizing long or complex content  

**How to use:**  
1. Right-click anywhere in Chrome.  
2. Select **Flow → Flowy Assistant**.  
3. Start chatting directly within your current tab context — Flowy understands the page you're on and works right where you need it.

*A seamless, focused AI experience — built right into your browser.*

DEMO -

https://github.com/user-attachments/assets/9dc60a38-ca05-476d-8cee-d6bf6abbbea2






## 2. Extension Popup Feature

### 🏠 Tab 1: Home  
A quick visual welcome and entry point to all features.

### 🎨 Tab 2: Color Palette

Whether you're designing a personal project, redecorating your space, or just love playing with color, this tool helps you create beautiful, meaningful palettes in seconds. Generate color schemes from your ideas, capture colors from any site, and explore AI insights like mood, cultural meaning, or design suitability. Plus, you’ll get practical tips for logos, websites, print, and even interior design—along with built-in accessibility checks to make sure your colors work for everyone.

- ✨ Generate color palettes from text prompts (“thoughts”)
- 🖌️ Capture colors from the current web page
- 💾 Save, edit, and manage favorite palettes
- 🤖 AI-powered insights:
  - 🎭 Mood of the palette
  - 🏭 Industry-specific suggestions
  - 🌏 Cultural significance
- 🛠️ Usage recommendations:
  - 🏷️ Logo integration
  - 💻 Responsive web design
  - 🖨️ Print and 🏠 interior design
- ♿ Accessibility analysis:
  - ⚖️ Contrast ratio (WCAG)
  - 👁️‍🗨️ Color blindness simulation
  - 🟢 Accessible alternatives

DEMO -


https://github.com/user-attachments/assets/763c9d1d-bd1c-450c-990a-8f0ffc1622f4



### 🔤 Tab 3: Font & Vector Generator

This tool empowers freelance designers, developers, and content creators to work faster and smarter. Whether you're building a client website or designing a brand identity, you can instantly generate font ideas and vector graphics from simple prompts—no need to search endless libraries. With live previews, one-click CSS or SVG copying, and direct page injection, it streamlines your creative workflow and helps you deliver polished results in record time.

- ✍️ Generate font suggestions from a text prompt
- 👀 Preview font cards with live samples
- 🪄 Apply a selected font to the current page (injects font into DOM)
- 📋 Copy font CSS for use elsewhere

- 🪄 Generate vector icons/graphics from a text prompt
- 👁️ Preview generated SVGs
- 📋 Copy SVG code or ⬇️ download SVG files

  DEMO -

https://github.com/user-attachments/assets/4e86ce1c-d4cb-48ea-b2af-9b56f90c7491



### 💸 Tab 4: Payment Management

This feature simplifies the entire payment process—freelancers can generate and send payment links directly to clients, track payment updates, and manage everything securely in one place. No more chasing payments. With easy API key management, freelancers can focus more on delivering work and less on administrative hassles powered by Razorpay Payments.

- 🔗 Generate payment links (Razorpay integration) and Send through Resend Toolkit
- 📊 Track payment status
- 🔐 Manage and save API keys securely
- 📋 View and manage all payment links
- 📧 Send payment Emails

DEMO -

https://github.com/user-attachments/assets/4f6d4856-a23a-4037-8607-41cb4c00914e




### 📝 Tab 5: Content Generation & Analysis

Whether you're a content writer, marketer, or solo business owner, this tool saves hours of work. Instantly create high-quality content for blogs, social media, proposals, or client emails—and refine it with AI-powered analysis. From SEO optimization to sentiment and engagement metrics, freelancers can ensure their content not only sounds great but performs well too. It’s your personal writing assistant, editor, and strategist in one.

- 🛠️ Generate content:
  - 📰 Blog posts, 🗞️ articles, 📨 newsletters, 📱 social posts
  - 📧 Business emails, 📄 proposals, 🏷️ product descriptions, 📚 case studies
- 🧠 Analyze content:
  - 😊 Sentiment, 🏷️ keywords, 📝 summary, ✏️ grammar
  - 🔍 SEO optimization, 📖 readability, 📈 engagement, 🏆 competitor analysis
- 📋 Copy generated or analyzed content

DEMO -

https://github.com/user-attachments/assets/88652dcf-ffb8-4f7a-b360-3bd0879a2c7e




### 🃏 Tab 6: Flashcard Generation

Whether you're a student, lifelong learner, or just curious, this tool makes it super easy to turn any article or webpage into study-friendly flashcards. With AI doing the heavy lifting, you get neatly structured cards with definitions, key points, and examples—ready to flip through, copy, or print. It's perfect for quick learning, test prep, or reviewing new topics on the fly.

- ⚡ Generate flashcards from any URL (or current tab)
- 🤖 AI-powered extraction and structuring
- 🃏 Interactive cards:
  - 🔄 Flip, ⏮️⏭️ navigate, 📋 copy, and 🖨️ export as PDF
- 📚 Structured answers: definitions, key points, examples, context

DEMO -

https://github.com/user-attachments/assets/f0dead21-0aa0-474e-a0ee-169ce10d2f80


## 🚀 Setup & Installation

### Backend Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in `.env`
3. Start the server:
   ```bash
   python main.py
   ```

### Extension Setup
1. Load the extension in Chrome:
   - Go to `chrome://extensions/`
   - Enable Developer mode
   - Click "Load unpacked"
   - Select the `FRONTEND` directory

## 📝 Notes
- Backend server must be running for full functionality
- All API endpoints require proper authentication
- Browser automation features require Chrome with debugging enabled


### Running The Extension

### 1. Backend Setup

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended/Optional)

#### Steps to Run Backend
1. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   cd BACKEND
   pip install -r requirements.txt
   ```
3. **Environment Variables**
   Create a `.env` file in the BACKEND directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   RESEND_API_KEY=your_resend_api_key
   ```

4. **Start the Server**
   ```bash
   python main.py
   ```
   The server will start on `http://localhost:5000`

### 2. Chrome Extension Setup

BACKEND/open_chrome.py - is a crucial utility script in the FLOW extension that enables automated browser control. It automatically launches Google Chrome with remote debugging capabilities on port 9222, creating a separate debugging profile to avoid interfering with your regular browser settings. 

The script is cross-platform compatible, working seamlessly on Windows, macOS, and Linux systems. It intelligently detects Chrome's installation path, manages existing browser instances, and ensures proper setup for automated tasks like screenshot capture, page analysis, and element interaction. This script is essential for the extension's automated features to function properly, providing a reliable foundation for browser automation and testing.

Before Starting the Chrome Extension, Run 
py -m open_chrome
OR
python -m open_chrome

Next, set up the extension:

In the Chrome browser.

1) Navigate to chrome://extensions/.

2) Enable Developer mode (toggle in the top-right corner).

3) Click Load unpacked.

4) Select the FRONTEND directory of the project folder.

5) The Extension Starts !! Yay!


