# Project Title
**Memory Pal** — Your AI Brain for Everything You've Ever Read

## Overview of the Idea

MemoryPal is your AI brain — a context-aware agent that instantly becomes an expert on any topic or company, using the data you provide.

Upload PDFs, emails, or web pages, and say:
“Be my business consultant for this startup.”
MemoryPal gets to work — pulling insights, tracking your questions, and citing sources.

It turns static agents into smart, searchable collaborators with:

📚 Persistent memory across sessions

🔍 Timeline-based recall

📎 Source-linked answers

- **Always learning**
- **Always growing**
- **Always ready to think with you**

## Project Goal
Our goal with MemoryPal is to demonstrate how agents can be transformed from short-term responders into long-term collaborators by giving them persistent, structured memory.

We aim to:

- **Show how agents can retain and recall knowledge across sessions, documents, and conversations.**

- **Prove the viability of combining RAG (Retrieval-Augmented Generation), pgvector-based search, and agent orchestration using the Agno framework — without relying on bulky stacks.**

- **Highlight how source-cited, memory-aware responses improve trust, usability, and real-world utility of AI assistants.**

- **Build a modular foundation that could scale into research assistants, legal aides, customer support agents, or even AI journaling tools.**

## How It Works

### 🧩 Core Functionality :
- **📥 PDF Ingestion: Chunk, embed, and store in Supabase**

- **🔎 Semantic Search: Find relevant document chunks via pgvector**

- **🧠 Agent Memory Timeline: Stores past questions, answers, and sources**

- **📂 Vaults: Organize memory by projects, clients, or topics**

- **📚 Source Citations: All responses cite the origin document/page**

- **🗂️ Relevant Response: All responses are retrieved from learning of document and then web search for less
hallucination**

- **💬 Conversational Agent: Built with Agno’s tools and memory-aware logic**

- **🖼️ Multimodal Ready: Structured text + PDF tables**

- **📚 Source Citations: All responses cite the origin document/page or web search**


## Tools Used

| Purpose       | Tool used                         |
| ------------- | --------------------------------- |
| Framework     | Agno (orchestration)              |
| Vector Store  | Supabase with pgvector            |
| Embeddings    | Mistral Embedder tool |
| Web search    | Serper API                        |
| PDF Parsing   | PyMuPDF (fitz)                    |
| UI            | Streamlit (MVP)                   |
| Storage       | Supabase (memory timeline, vaults)|



## UI Approach



<img width="959" alt="Image" src="https://github.com/user-attachments/assets/a5d3c0eb-1eb2-4ed0-b683-d705e3418b21" />


## Visuals
Below is architectural workflow diagram of Meomory Pal agent :

<img width="471" alt="Image" src="https://github.com/user-attachments/assets/2c5335ae-2eba-4cfe-ab81-90bf8ba5f111" />



## Additional Notes
1) Modular architecture — easy to plug in other vector DBs (Weaviate, Qdrant)

2) Entire stack is native Agno and custom tools

3) Scalable with auto-tagging and multi-agent extensions (e.g., SummarizerAgent, TimelineAgent)

4) Future scope: Ready to extend to voice (OpenAI Whisper) or images (OCR/Donut) and workspaces.


## ✅ What MemoryPal Solves:

- **🗂️ No More Starting Over: Users can build and reuse memory over time — including documents, questions, answers, and sources.**

- **📎 Persistent, Project-Based Context: MemoryPal remembers what you uploaded, what you asked, and what it answered — across sessions.**

- **🔍 Reliable Retrieval with Citations: Combines RAG + semantic memory to give context-aware, source-grounded responses.**

- **💼 Real-World Use Cases: Ideal for startups, consultants, lawyers, researchers — anyone who works with lots of documents and wants a smart, searchable AI assistant.**


## 🏗️ Architecture
```
[User uploads PDF]
        ↓
[Agent embeds & stores vectors in Supabase]
        ↓
[User asks: "What is ClientX’s refund policy?"]
        ↓
[Agent retrieves relevant chunks from vector DB]
        ↓
[Agent generates answer + cites source]
        ↓
[Memory timeline logs Q&A + source]

```

## 📋 Setup Instructions

### Prerequisites
- Python 3.12+
- Supabase account (just to see content in db or else no need)
- SERPER API key
- MISTRAL API key
- GROQ API key
- OPENAI API key

### Environment Variables
Create a `.env` file with the following variables:

```env
# MISTRAL (embedder)
MISTRAL_API_KEY=your_mistral_api_key

# OPENAI (Chunking)
OPENAI_API_KEY=your_openai_api_key

# GROQ API key (llm provider)
GROQ_API_KEY=your_groq_api_key

# SERPAPI Web Search
SERPAPI_KEY=your_serper_api_key

# SUPAASE ACCOUNT (If you want to see content in db or else no need)
SUPABASE_KEY=your_supabase_key
SUPABASE_DB_PASSWORD=your_supabase_db_password
SUPABASE_URL=your_supabase_url

```

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Supabase**
   - If you want to see content in database or else no need
   - Create Supabase account and upload required key, url, password of the database


4. **Change Directory**
   ```bash
   cd .\submissions\Memory-Pal

   ```
5. **Run Streamlit App (MVP)**
   ```bash
   python -m streamlit run app.py
   ```

6. **Upload .assets folder pdf for refernce use**
   ```
   in Streamlit UI upload this two pdfs financials.pdf and pitch_deck.pdf and you can use prompt.md for refernce or your own prompt (as you wish)

   or prompt: “Based on our pitch_deck.pdf and financials.pdf, what are the major risks an investor might flag?”

   ```
