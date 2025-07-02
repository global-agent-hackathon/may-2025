# 🚀 Flux: AI-Powered Form Builder with Intelligent Agents

> **Next-generation form platform** powered by intelligent agents, multi-step tool use, and persistent memory. Transform natural language into sophisticated forms with AI-driven insights and automation.

## 🎯 Quick Start

## 🎥 Demo Videos

### Demo Video 1
[Watch Demo Video 1](flux-main/public/out.mp4)

### Demo Video 2
[Watch Demo Video 2](flux-main/public/demo.mp4)

// ... existing code ...

### Prerequisites
- **Node.js 18+** or Bun
- **Python 3.8+**
- **PostgreSQL** database (or use [Neon.tech](https://neon.tech) for serverless Postgres)

### 🏃‍♂️ Running the Projects

#### 1. Backend (AI Agent API) - `flux-agent`
```bash
cd flux-agent

# Setup virtual environment and install dependencies
make setup
# Activate the virtual environment
source venv/bin/activate

# (Optional) If you update requirements.txt later:
make install

# Set up environment (see Environment Setup below)
cp .env.example .env
# Edit .env with your API keys

# Run the API
make run
# For development with auto-reload:
# make run-dev
```
**Backend runs on:** `http://localhost:8000`

#### 2. Frontend (Next.js App) - `flux-main`
```bash
cd flux-main

# Install dependencies
npm install
# or: bun install

# Set up environment (see Environment Setup below)
# Edit .env with your configuration

# Run database migrations
npx prisma migrate dev

# Start development server
npm run dev
# or: bun dev
```
**Frontend runs on:** `http://localhost:3000`

---

## 🔧 Environment Setup

### Backend Environment (`flux-agent/.env`)
```env
# API Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development

# 🤖 AI Service API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
MEM0_API_KEY=your_mem0_api_key_here

# 🔥 Web Scraping
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# 🗄️ Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# 📊 Logging
LOG_LEVEL=INFO
DEBUG=false
```

### Frontend Environment (`flux-main/.env`)
```env
# 🗄️ Database (same as backend)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# 🔐 Authentication (Clerk)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key
CLERK_SECRET_KEY=sk_test_your_key
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/auth/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/auth/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# 🔗 Backend Connection
AGENT_API_URL=http://localhost:8000
```

---

## ✨ Features

### 🧠 **AI-Powered Form Generation**
- **Natural Language Processing**: Describe your form in plain English
- **Intelligent Field Detection**: Automatically suggests appropriate field types
- **Context-Aware Generation**: Understands business requirements and user intent
- **Smart Validation**: Auto-generates validation rules based on field purpose

### 🤖 **Advanced AI Agents**
- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Form Generation Agent**: Creates sophisticated forms from natural language
- **SQL Analysis Agent**: Converts questions into database queries
- **Analytics Agent**: Generates insights and chart recommendations
- **Memory Agent**: Maintains context across conversations

### 🧮 **AI Field Computation**
- **Dynamic Value Calculation**: Fields that compute values based on other inputs
- **Web Content Integration**: Scrapes and analyzes external URLs for context
- **Sentiment Analysis**: Automatic sentiment scoring of text responses
- **Custom AI Logic**: Define complex business rules with natural language

### 📊 **Intelligent Analytics**
- **Text-to-SQL Queries**: Ask questions about your data in natural language
- **Auto-Generated Charts**: AI suggests the best visualizations for your data
- **Batch Data Analysis**: Process large datasets with intelligent insights
- **Real-time Insights**: Live analytics as responses come in

### 🧠 **Persistent Memory System**
- **Conversation Memory**: Remembers past interactions and preferences
- **Form Evolution Tracking**: Learns from form modifications over time
- **User Context Awareness**: Adapts to individual user patterns
- **Cross-Session Continuity**: Maintains context across multiple sessions

### 🏢 **Workspace Management**
- **Multi-Workspace Organization**: Separate forms by projects or teams
- **Collaborative Features**: Share workspaces with team members
- **Favorites System**: Quick access to frequently used forms
- **Smart Search**: Find forms across all workspaces instantly

### 🗑️ **Advanced Form Management**
- **30-Day Soft Delete**: Trashed forms recoverable for 30 days
- **Version Control**: Track form changes and evolution
- **Draft/Live States**: Seamless publishing workflow
- **Bulk Operations**: Manage multiple forms efficiently

---

## 🎨 **User Experience Flow**

### 🚀 **Onboarding Journey**
1. **Sign Up** → Secure authentication with Clerk
2. **Create Workspace** → Organize your forms by project
3. **Describe Your Form** → Natural language input
4. **AI Generation** → Watch your form come to life
5. **Customize & Publish** → Fine-tune and go live

### 💡 **Form Creation Magic**
```
"Create a customer feedback form for our restaurant with sentiment analysis"
                                    ↓
🤖 AI analyzes requirements → Generates form structure → Adds AI fields
                                    ↓
📝 Beautiful form with rating scales, text areas, and auto-sentiment scoring
```

### 📈 **Data Analysis Workflow**
```
"What's the average satisfaction score this month?"
                    ↓
🔍 AI converts to SQL → Executes query → Generates insights
                    ↓
📊 Interactive charts and detailed analysis
```

### 🔄 **Continuous Learning**
- **Memory Integration**: Each interaction improves future suggestions
- **Pattern Recognition**: Learns your form creation preferences
- **Smart Recommendations**: Suggests improvements based on usage patterns

---

## 🏗️ **Technical Architecture**

### **Frontend Stack**
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + Shadcn UI components
- **State Management**: Zustand + TanStack Query
- **Authentication**: Clerk
- **Database**: PostgreSQL with Prisma ORM
- **Charts**: Recharts + Chart.js

### **Backend Stack**
- **Framework**: FastAPI (Python)
- **AI Orchestration**: Agno agents
- **Language Models**: OpenAI GPT-4, Groq Llama
- **Memory**: Mem0 for persistent context
- **Web Scraping**: Firecrawl
- **Database**: PostgreSQL with async drivers

### **AI Capabilities**
- **Multi-Model Support**: OpenAI, Groq, Anthropic
- **Agent Coordination**: Specialized agents for different tasks
- **Memory Persistence**: Long-term context retention
- **Tool Integration**: Web scraping, database queries, analytics

---

## 🎯 **Why Flux?**

### **For Businesses**
- ⚡ **10x Faster** form creation than traditional builders
- 🧠 **Intelligent Insights** from response data automatically
- 🔄 **Adaptive Forms** that improve based on user feedback
- 📊 **Advanced Analytics** without technical expertise

### **For Developers**
- 🏗️ **Clean Architecture** with proper separation of concerns
- 🔌 **Extensible Agent System** for custom AI workflows
- 📚 **Comprehensive APIs** for integration
- 🛠️ **Modern Tech Stack** with best practices

### **For Users**
- 🎨 **Intuitive Interface** that feels natural
- 🚀 **Instant Results** from AI-powered generation
- 📱 **Responsive Design** works on all devices
- 🔒 **Enterprise Security** with Clerk authentication

---

## 📚 **API Documentation**

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 **Contributing**

We welcome contributions! Please check our contribution guidelines and feel free to submit issues or pull requests.

## 📄 **License**

MIT License - see LICENSE file for details.

---

**Built for the Global Agent Hackathon** - Showcasing the future of agentic reasoning, persistent memory, and intelligent form automation.

> *Transform how you think about forms. Transform how forms think about data.* 