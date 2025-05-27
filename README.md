# 🚀 PolyTutor

**PolyTutor** is an AI-powered, multi-agent tutoring platform designed to deliver personalized, subject-specific learning experiences in **Physics**, **Chemistry**, **Mathematics**, and **Languages**. Powered by advanced LLMs, real-time streaming, and smart agent orchestration, PolyTutor transforms the way learners engage with complex concepts.

---

## 🌟 Key Features

### 🎓 Multi-Subject Intelligence

* **Physics**: Interactive problem-solving, concept visualization, and foundational explanations.
* **Chemistry**: Molecular structures, chemical reactions, and theoretical concepts.
* **Mathematics**: Step-by-step equation solving, concept breakdowns, and logical reasoning.
* **Language Learning**:

  * Grammar breakdowns
  * Vocabulary builders
  * Pronunciation helpers
  * Cultural context & idioms
  * Real-world practice dialogues
  * Support for multiple languages (English, Spanish, French, German, Italian, Japanese, Chinese, danish)

### 🧠 Intelligent Interactions

* Real-time streaming of responses
* Markdown-formatted outputs for seamless UI rendering
* Smart subject-switching suggestions
* Dark/Light mode support
* Upload notes and PDFs for contextual learning
* Contextual search via vector embeddings (LanceDB + OpenAI)

---

## 🧱 System Architecture

![Architecture Diagram](./images/Poly_AI%20\(3\).jpeg)

PolyTutor uses a **multi-agent orchestration framework** to deliver domain-specific tutoring sessions, backed by OpenAI’s GPT models and a powerful document/vector search layer.

### 🔁 Core Workflow

1. **Frontend (React + Vite + TailwindCSS)**

   * Clean user interface for prompt entry and visual display.
   * Interactions trigger API calls to the backend via HTTPS.

2. **Backend (FastAPI + Streaming)**

   * Manages real-time communication with users.
   * Routes queries to the Agno agent system.
   * Streams incremental results using `StreamingResponse`.

3. **Agno Orchestrator**

   * Acts as the system brain, routing tasks to appropriate agents.
   * Maintains state, context, and user preferences.

4. **Domain Validator Agent**

   * Ensures user prompt matches a supported subject.
   * If mismatched, prompts user to rephrase or redirect.

---

## 🤖 Specialized Agent System

### 🗣️ Language Agents

| Agent                  | Function                                                    |
| ---------------------- | ----------------------------------------------------------- |
| **Grammar Coach**      | Teaches grammar using target language and English examples. |
| **Vocabulary Builder** | Generates word lists with usage examples.                   |
| **Cultural Expert**    | Explains cultural idioms and expressions.                   |
| **Dialogue Agent**     | Crafts practice dialogues for real-world scenarios.         |

### 🧪 STEM Agents

| Agent                    | Function                                             |
| ------------------------ | ---------------------------------------------------- |
| **Concept Agent**        | Step-by-step conceptual teaching with examples.      |
| **Visual Agent**         | Returns visuals, equations, or prompts for diagrams. |
| **Problem Solver Agent** | Solves and explains problems clearly.                |

---

## 🔍 Knowledge Integration

* Upload PDFs, slides, or text notes.
* Vectorized using OpenAI embeddings + LanceDB.
* Enables in-context answers referencing your personal knowledge base.
* Search options:

  * **Database Only**
  * **Web (DuckDuckGo) + YouTube**
* New results get cached into the vector DB for faster reuse.

---

## 📡 Real-Time Experience

PolyTutor streams responses incrementally:

```
[Validating prompt...]
[Routing to Chemistry Agents...]
[Searching uploaded files...]
[Generating answer...]
```

Final output is markdown-formatted — perfect for rich interfaces or PDF export.

---

## 🧰 Tech Stack

### ⚙️ Frontend

| Tool               | Purpose                    |
| ------------------ | -------------------------- |
| React + TypeScript | UI & state management      |
| Vite               | Build tooling & hot reload |
| TailwindCSS        | UI styling                 |
| Shadcn UI          | Prebuilt UI components     |
| Lucide Icons       | Clean vector icons         |
| React Markdown     | Render Markdown safely     |

### 🔧 Backend

| Tool             | Purpose                                   |
| ---------------- | ----------------------------------------- |
| Python + FastAPI | Web server & API                          |
| Agno AI SDK      | Agent orchestration                       |
| Streaming        | Real-time message updates to frontend     |
| LanceDB          | Vector search for user-uploaded documents |
| OpenAI GPT-4o    | Core reasoning engine                     |

---

## 🗂️ Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   └── repositories/
│   └── requirements.txt
│
└── query-pilot-chat/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   └── styles/
    ├── public/
    └── package.json
```

---

## 🚀 Getting Started

### 📦 Prerequisites

* Node.js (v16+)
* Python 3.8+
* Git

---

### 🖥️ Frontend Setup

```bash
cd query-pilot-chat
npm install
npm run dev
```

---

### 🧪 Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🔐 Environment Variables

### Backend `.env`

```env
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_endpoint_url
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_DEPLOYMENT_NAME=your_deployment
```

### Frontend `.env`

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 🤝 Contributing

We welcome contributions to make PolyTutor even more powerful.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a Pull Request

---

## 👥 Team

| Name                    | Role                   |
| ----------------------- | ---------------------- |
| **Nandish Shah**        | AI & Backend Architect |
| **Joseph Kimani Kamau** | Frontend & UX Engineer |

---

## 🙏 Acknowledgments

* **OpenAI** for powerful LLMs
* **Agno** for agent orchestration
* **Shadcn UI** for the modern component system
* **FastAPI** for blazing-fast backend
* **LanceDB** for vector storage and retrieval

