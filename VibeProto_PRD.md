## 1. Overview
VibeProto is an innovative AI-powered tool designed to democratize software development by enabling non-technical users to create prototypes and automate tasks using natural language. Leveraging advanced AI models like OpenAI's GPT-4 and the Agno framework for agent-based storage and reasoning, VibeProto transforms simple text descriptions into functional code, such as Python scripts or web app prototypes. The system now features cloud-based remote agents that can process tasks in the background, even when users are offline. This PRD outlines the requirements for the current release and future enhancements, aiming to bridge the gap between technical expertise and accessibility for all users. The project is being developed as part of a hackathon submission, with a focus on user-friendly design and robust backend integration.

## 2. Objectives
- **Primary Objective**: Enable non-technical users to generate functional software prototypes (e.g., Python scripts, web apps) using natural language inputs within minutes.
- **Secondary Objectives**:
  - Integrate Agno's storage and agent capabilities to persist session data and improve user experience.
  - Enhance code generation quality using optimized AI prompts (e.g., from Codex CLI).
  - Develop a chat-like interface with a code display area to make the tool intuitive and engaging.
  - Ensure scalability and security for future expansion and hackathon submission.
- **Long-Term Goal**: Establish VibeProto as a leading tool for AI-assisted prototyping, accessible to a global audience.

## 3. Target Audience
- **Primary Audience**: Non-technical individuals, including hobbyists, small business owners, and educators, who lack coding skills but need to create prototypes or automate tasks.
- **Secondary Audience**: Junior developers and designers seeking a rapid prototyping tool to iterate ideas before full development.
- **Tertiary Audience**: AI enthusiasts and hackathon participants interested in experimenting with natural language processing and agent-based systems.
- **User Characteristics**:
  - Age range: 16-60.
  - Tech literacy: Basic to intermediate.
  - Needs: Accessibility, ease of use, and quick results.

## 4. Features
### Current Features
- **Natural Language Input**: Users can describe prototypes (e.g., "A script to download images") in plain English.
- **Code Generation**: Generates Python scripts or web app prototypes using OpenAI's GPT-4 with direct API integration.
- **Prototype Type Selection**: Dropdown to choose between automation scripts and web apps.
- **Session Storage**: Uses SQLite to persist user sessions and prompts.
- **Think Feature**: Real-time display of AI reasoning during code generation.
- **API Key Management**: Secure interface for managing OpenAI and Anthropic API keys.
- **Enhanced Error Handling**: Comprehensive error feedback for API and generation issues.
- **Remote Agent System**: Cloud-based background processing allowing tasks to continue running even when users are offline or their device is closed.
- **Parallel Task Processing**: Support for running multiple tasks (up to 10 agents) simultaneously in the background.
- **Docker Deployment**: Containerized setup for easy cloud deployment and scalability.
- **Task Delegation**: Users can delegate complex or time-consuming tasks to remote agents and retrieve results later.

### Next Features (Upgrades)
- **Chat-Like Interface**: Replace the current layout with a ChatGPT-style interface, featuring a left sidebar for session management and code display.
- **Enhanced Code Display**: Add copy and download buttons for generated code in the sidebar.
- **Prompt Optimization**: Integrate Codex CLI system prompts to improve code generation quality.
- **Multi-Language Support**: Extend generation to JavaScript and HTML/CSS for web apps.
- **Real-Time Feedback**: Provide inline suggestions or error checks during prompt input.

### User Experience & Interface
- **Minimalist Design**: Clean, intuitive interface with minimal cognitive load
- **Responsive Layout**: Mobile-first design that adapts to all screen sizes
- **Session Management**: Easy access to previous prompts and generated code
- **Error Handling**: Clear feedback for API limits, invalid inputs, or generation failures
- **Accessibility**: WCAG 2.1 compliance for broader user inclusion
- **Performance**: Sub-second response times for UI interactions, clear loading states for generation 

## 5. Updates Log

### Update - March 20, 2024
#### Major Changes
1. **Remote Agent System Implementation**
   - Added cloud-based background processing functionality
   - Implemented a pool of up to 10 concurrent agent workers
   - Tasks continue running even when users are offline
   - Added task queuing and status tracking

2. **Docker Containerization**
   - Created Dockerfile for containerizing the application
   - Added docker-compose.yml for easy deployment
   - Configured volume mounting for persistent data

3. **User Interface Enhancements**
   - Added Remote Mode toggle in the UI
   - Implemented background task status checking
   - Added task completion notifications
   - Created visual indicators for remote task status

#### Technical Implementations
- **RemoteAgentPool**: A thread-safe agent pool that manages task submission, queuing, and execution
- **RemoteTask**: An object representing a task with status tracking and result storage
- **Background Processing**: Tasks run in separate threads to allow parallel execution
- **Status Tracking**: Periodic status checks for remote tasks with automatic UI updates
- **Docker Configuration**: Multi-container setup with separate services for frontend and backend
- **Volume Mounting**: Persistent storage for database and task data

#### Impact
- Non-technical users can now start complex generations and return later for results
- Reduced resource requirements on user devices
- Improved ability to handle multiple tasks simultaneously
- Enhanced robustness in unstable network environments
- Simplified deployment for cloud environments

### Update - March 19, 2024
#### Major Changes
1. **Direct OpenAI Integration**
   - Removed dependency on agno package
   - Implemented direct OpenAI API calls for enhanced reliability
   - Added support for both OpenAI and Anthropic API keys

2. **Think Feature Implementation**
   - Added real-time display of AI reasoning during code generation
   - Implemented staged updates to show thinking process
   - Enhanced user feedback during code generation

3. **Settings Interface**
   - Added new modal for API key management
   - Implemented secure key storage
   - Added validation for API keys

4. **UI/UX Improvements**
   - Added thinking animation with dots
   - Enhanced error feedback
   - Improved session management interface

#### Technical Updates
- Refactored backend to use direct OpenAI API calls
- Enhanced prompt endpoint now uses direct OpenAI integration
- Improved error handling throughout the application
- Added new styling for think feature and settings modal

#### Impact
- Improved reliability of code generation
- Enhanced user experience with real-time feedback
- Better error handling and user guidance
- More secure API key management 