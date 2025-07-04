<p align="center">
  <img src="./src/assets/logo.png" alt="Clippy Logo" width="150">
</p>

<h1 align="center">🔍 Clippy – Your Cross-Platform Smart Search Butler</h1>

<p align="center">
  <i>Your personal AI-powered assistant, beautifully blending a lightning-fast search interface with intelligent agent capabilities.</i>
</p>

<p align="center">
  <b>✨ Search files instantly • 📁 Summarize files • 💬 Get concise answers • 🤖 Run terminal commands • 🎯 Stunning native UI</b>
</p>

---

## 🎬 See Clippy in Action!

<p align="center">
  <a href="https://www.youtube.com/watch?v=D_rcu602wCc" target="_blank" style="text-decoration:none;">
    <span style="display:inline-block; border:3px solid #9b87f5; border-radius:12px; padding:24px 32px; background:#181c2a; color:#fff; font-size:1.3rem; font-weight:bold; letter-spacing:1px;">
      🚀 Watch the Clippy Demo on YouTube
    </span>
  </a>
</p>

<p align="center">
  <b>👆 Click above to see Clippy instantly search, summarize, and supercharge your workflow!</b>
</p>

## 🧠 Features

- 🔎 **Smart Search**  
  Type anything to trigger intelligent file and app search with instant results.

- 🧠 **AI Assistant**  
  Press `Ctrl + Enter` on a file to get a fast, AI-powered summary.

- 💬 **Universal Input**  
  Press `Enter` to communicate with the agent — ask questions, get definitions, or perform quick tasks.

- 💻 **Simple Commands**  
  Use `Enter` to run safe, general-purpose commands like `create react app`, `create file notes.txt`, or `open chrome`.

- 🗂 **Instant Launch**  
  Press `Shift + Enter` to open files or apps directly from the search.

- 🛠️ **Project Creation**  
  Instantly scaffold files, folders, or full projects (like Vite/React apps) from the interface.

- 🌐 **Environment Info**  
  Retrieve and view your system's environment details instantly.

- 🖥️ **Native UI**  
  Built with Flet — elegant, minimal, and frameless native desktop experience.

- 🪄 **Focused Results**  
  Output is concise, relevant, and designed for speed and utility.

- 🔌 **Cross-Platform**  
  Fully supported on MacOS and Windows with complete agent tools and UI. Linux support coming soon.
  
  > **Update:** Clippy is now available for Windows with a global shortcut (`Ctrl + Space`)! Use the native wrapper for instant access from anywhere. See below for setup instructions.

## 🖥️ Platform Support Status

### ✅ Windows (Fully Supported)
- ✅ Cover agent tools and UI - **COMPLETE**
- ✅ File search and indexing - **COMPLETE**
- ✅ Global shortcut (`Ctrl + Space`) and overlay - **NOW AVAILABLE**
- ✅ Native wrapper - **Build and use ClippyWindowNative for global shortcut**

### ✅ macOS (Fully Functional)
- ✅ All functionality complete and working
- ✅ Native wrapper ready - open `MACOS Native/Clippy/Clippy.xcodeproj` and run
- ⚠️ Cannot provide published apps due to non-premium developer account
- 🔧 Manual build required (see installation steps below)

### 📋 Linux (Planned)
- 📋 Support planned for future releases

## 🧠 Smart Implementation

<p align="center">
  <img src="./src/assets/clippy-alpha3-multi-agent.gif" alt="Main Agent Workflow" width="600">
</p>

Clippy is designed with a highly intelligent architecture to provide seamless and efficient user interactions:

- **Team Agent Routing**: Clippy uses the Team Agent as a router to intelligently redirect user prompts to either the General Purpose Agent (GAP) or the Terminal Agent (TER) based on the context of the request.
- **Terminal Agent (TER)**:
  - Adapts to the local environment by loading shell profiles, ensuring compatibility with the user's system.
  - Executes subprocesses and smartly appends `yes` or `-y` to commands for zero user intervention, making operations like installations completely hands-free.
- **General Purpose Agent (GAP)**: Equipped with web search capabilities, it can fetch information from the internet to provide accurate and context-aware responses.
- **Shared Memory**: All agents share a common memory, enabling smooth back-and-forth communication. This is particularly useful for complex terminal operations, such as creating a React app, where the General Purpose Agent can suggest a name, and the Terminal Agent can execute the command seamlessly.
- **Cross-Platform System Directory Access**: Clippy includes a cross-platform method to retrieve system directories like Documents, Desktop, Downloads, etc., allowing users to act on these directories with ease, such as organizing files or performing batch operations.

Clippy's architecture ensures a cohesive and intelligent experience, making it a powerful tool for both casual and advanced users.

---

## 🖼️ New: Multimodal File Summarization (Ctrl+Enter Magic!)

🚀 **Clippy just got a major upgrade!**

Now, with a simple <kbd>Ctrl</kbd> + <kbd>Enter</kbd> on any file in your search results, you can instantly generate a smart summary—no matter the file type. Whether it's a PDF, image, audio, video, or even a non-standard/binary file, Clippy's new multimodal agent will analyze and summarize it for you in seconds.

- **Universal Summarization:** Summarize PDFs, images, audio, video, and even raw data from non-standard files. If Clippy can't natively parse the file, it will attempt to extract and summarize the raw text content for you.
- **Popup Power:** The summary appears in a beautiful, scrollable popup—no clutter, just clarity. Instantly open the file from the popup if you want to dive deeper.
- **Lightning Fast:** Just select a file and hit <kbd>Ctrl</kbd> + <kbd>Enter</kbd>—Clippy does the rest. No menus, no drag-and-drop, just pure productivity.
- **User-Friendly:** If you try to summarize a directory or an unreadable file, Clippy will let you know with a friendly message—no crashes, no confusion.

🎉 **This is a game-changing feature that every user (and hackathon judge!) will love.**

Give it a try and experience the future of file intelligence—right from your keyboard!

---

## 🖥️ Why Native Wrapper?

The native wrapper is a crucial part of Clippy's architecture, providing the following benefits:

- **Global Key Implementation**: Enables the use of global hotkeys, allowing Clippy to be triggered instantly from anywhere on your system.
- **Overlay Permissions**: Grants the ability to overlay Clippy on top of any app or screen, ensuring seamless accessibility without disrupting your workflow.

These features make Clippy a truly integrated and efficient tool for your desktop environment.

---

## 📸 Sneak Peek

<p align="center">
  <img src="./src/assets/terminal_command.png" alt="Python Environment Version" width="600">
  <h4 align="center">🎯 Example: Quickly check your Python environment version</h4>
  <p align="center"><i>Clippy helps developers save time by instantly retrieving environment details without needing to open a terminal manually.</i></p>
</p>

<p align="center">
  <img src="./src/assets/terminal_command2.png" alt="Create Text File" width="600">
  <h4 align="center">📂 Example: Create a text file in your Documents folder</h4>
  <p align="center"><i>Perfect for users who need to quickly jot down notes or create files in specific directories without navigating through multiple menus.</i></p>
</p>

<p align="center">
  <img src="./src/assets/terminal3.png" alt="General Purpose Agent Task" width="600">
  <h4 align="center">💬 Example: Get quick answers using the General Purpose Agent</h4>
  <p align="center"><i>Clippy acts as your personal assistant, providing concise answers to questions, definitions, or even code snippets in seconds.</i></p>
</p>

<p align="center">
  <img src="./src/assets/file_browse.png" alt="Open Apps and Files" width="600">
  <h4 align="center">🖥️ Example: Open apps, files, and folders with ease</h4>
  <p align="center"><i>Clippy simplifies your workflow by letting you open frequently used apps or files instantly, saving you from searching through your system.</i></p>
</p>

---

## 🚀 Getting Started


### Prerequisites

**For Windows Users**: 
Files are not indexed by default in Windows. You'll need to install Everything CLI for enhanced file indexing and searching:

1. Download and install Everything from: https://www.voidtools.com/downloads/
2. This provides fast file indexing that Clippy leverages for lightning-fast search results

### Installation Steps

1. **Clone this Repo**

   ```bash
   git clone https://github.com/smil-thakur/global-agent-hackathon-may-2025.git
   cd submissions/Clippy
   ```

2. **Install Requirements**

   We recommend using a virtual environment:

   **For Windows:**
   ```bash
   python -m venv clippyENV
   clippyENV\Scripts\activate
   pip install -r requirements-win.txt
   ```

   **For macOS:**
   ```bash
   python -m venv clippyENV
   source clippyENV/bin/activate
   pip install -r requirements.txt
   ```

3. **Setup .env**

   Create a `.env` file and add your Gemini API Key:

   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the App**

   ```bash
   python src/main.py
   ```

   **Note**: By default, Clippy runs as a web app accessible at `localhost:8550`. To run as a simple desktop app without browser dependency, edit `main.py` and uncomment/comment the last lines as indicated in the code.


### 🏗️ Building Executable

#### Windows

Clippy for Windows now supports a global shortcut (`Ctrl + Space`) using the native wrapper! To use this feature, follow these steps:

1. **Install PyInstaller and build the main Clippy frontend:**
   ```bash
   pip install pyinstaller
   pyinstaller Clippy-win.spec
   ```
   This will generate `Clippy.exe` in the `dist` folder. This EXE serves as the main frontend web server that the native wrapper will launch and wrap.

2. **Build the native wrapper for global shortcut and overlay:**
   - Open the `ClippyWindowNative` project in Visual Studio.
   - Build the project (this creates a native Windows EXE with global shortcut support).
   - Run the resulting EXE. It will launch Clippy and allow you to trigger it from anywhere using `Ctrl + Space`.

> **Note:** Make sure you have built `Clippy.exe` (step 1) before running the native wrapper, as the wrapper depends on it to serve the Clippy UI.

The native wrapper provides global shortcut and overlay functionality, making Clippy instantly accessible on Windows.

#### macOS
To create a native macOS app:

1. **Build the Python app**
   ```bash
   pip install pyinstaller
   pyinstaller Clippy-mac.spec
   ```

2. **Run the native wrapper**
   - Navigate to `MACOS Native/Clippy/`
   - Open `Clippy.xcodeproj` in Xcode
   - Build and run the project

3. **Install the app**
   - Place the built `.app` file in your Applications folder
   - The native wrapper provides global shortcuts and overlay functionality

**Note**: Due to non-premium developer account limitations, pre-built apps cannot be distributed. However, all functionality is complete and works when built locally.

> ⚠️ **Development Note**: The setup process is currently under active development. Some dependencies and steps may change as we approach the final release. We plan to consolidate all setup steps into a single script for easier installation.

---

## 📁 Project Structure

<ul>
  <li><strong>MACOS Native/</strong>
    <ul>
      <li><strong>Clippy/</strong>
        <ul>
          <li><strong>Clippy/</strong>
            <ul>
              <li><strong>AppDelegate.swift</strong> – App delegate for macOS native app</li>
              <li><strong>Assets.xcassets/</strong> – App icons and assets</li>
              <li><strong>Base.lproj/Main.storyboard</strong> – Main storyboard for UI</li>
              <li><strong>Clippy.entitlements</strong> – App entitlements</li>
              <li><strong>Info.plist</strong> – App configuration</li>
              <li><strong>ViewController.swift</strong> – Main view controller</li>
            </ul>
          </li>
          <li><strong>Clippy.xcodeproj/</strong> – Xcode project files</li>
        </ul>
      </li>
    </ul>
  </li>
  <li><strong>src/</strong>
    <ul>
      <li><strong>agents/</strong>
        <ul>
          <li><strong>agentsUtility.py</strong> – Utility functions for agents</li>
          <li><strong>mainAgent.py</strong> – Main agent logic</li>
        </ul>
      </li>
      <li><strong>agentTools/</strong>
        <ul>
          <li><strong>agentTools.py</strong> – Tools for agent integration</li>
        </ul>
      </li>
      <li><strong>assets/</strong> – App assets like icons and logos</li>
      <li><strong>components/</strong>
        <ul>
          <li><strong>aiResponseContainer.py</strong> – AI response container</li>
          <li><strong>resultSection.py</strong> – Result section component</li>
          <li><strong>resultSectionContainer.py</strong> – Container for result sections</li>
        </ul>
      </li>
      <li><strong>enums/</strong>
        <ul>
          <li><strong>commonExtension.py</strong> – Common file extensions</li>
        </ul>
      </li>
      <li><strong>states/</strong>
        <ul>
          <li><strong>thinkingStates.py</strong> – States for AI thinking</li>
        </ul>
      </li>
      <li><strong>utilities/</strong>
        <ul>
          <li><strong>checkPermissions.py</strong> – Permission checking utility</li>
          <li><strong>debouncer.py</strong> – Input debouncer utility</li>
          <li><strong>fileUtils.py</strong> – File-related utilities</li>
          <li><strong>getResourcePath.py</strong> – Resource path resolver</li>
          <li><strong>listSorter.py</strong> – List sorting utility</li>
          <li><strong>openApp.py</strong> – Utility to open apps</li>
          <li><strong>searchUtils.py</strong> – Search-related utilities</li>
        </ul>
      </li>
      <li><strong>main.py</strong> – Main entry point of the app</li>
    </ul>
  </li>
  <li><strong>memory.db</strong> – Local database for memory</li>
  <li><strong>requirements.txt</strong> – Python dependencies (general)</li>
  <li><strong>requirements-win.txt</strong> – Windows-specific Python dependencies</li>
  <li><strong>Clippy-win.spec</strong> – PyInstaller spec file for Windows executable</li>
  <li><strong>Clippy-mac.spec</strong> – PyInstaller spec file for macOS app</li>
  <li><strong>README.md</strong> – You are here!</li>
  <li><strong>pyproject.toml</strong> – Python project configuration</li>
  <li><strong>pyrightconfig.json</strong> – Pyright type-checking configuration</li>
</ul>

---

## 🧩 Tech Stack

- 🐍 **Python**
- 💻 **Flet** – Native cross-platform UI framework
- 🧠 **Agno Agent** https://www.agno.com/
- 🪄 **Gemini API** (via Agno Models)
- ⚙️ **Asyncio, Debouncing, File system search, and more**

---

## 🎯 Vision

We're building the next-gen AI-powered Spotlight for your desktop – a hybrid between a blazing-fast search tool and a context-aware assistant. This is just the beginning. In the future, ClippyAI will include:

- 🔊 **TTS Summarization of Documents**: Provide audio summaries of documents for accessibility and convenience.
- 🧠 **Local Memory for Smarter Interactions**: Enhance context retention for more personalized and efficient responses.
- 📦 **Plugin Architecture**: Allow users to extend Clippy's functionality with custom plugins.

ClippyAI aims to redefine how users interact with their desktop environment by combining speed, intelligence, and adaptability.

---

## 🤝 Contributing

Got an idea? PRs welcome!
Open an issue or drop your suggestions.

---

## 🏆 Hackathon Participation

https://github.com/global-agent-hackathon/global-agent-hackathon-may-2025

This project is being developed as part of the Global Agent Hackathon – May 2025. Let's build the future of intelligent agents, one utility at a time.

---

## 📬 Contact

Feel free to reach out or connect on GitHub if you'd like to collaborate or contribute!

---

