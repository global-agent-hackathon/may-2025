# Intersectx

Intersectx is an AI-powered platform for comprehensive company analysis and investment insights, inspired by platforms like Crunchbase. The application consists of a modern React-based frontend and a robust, agentic backend, working together to deliver advanced research, chat, and analytics capabilities.

## Overview

- **Frontend**: A React + TypeScript web app for users to search companies, view analytics, chat with AI, and conduct research.
- **Backend**: A FastAPI-based service orchestrating multiple AI agents, handling data, chat, research, and integration with external sources.

---

## Key Features

- **Company Search & Analysis**: Discover and analyze companies with detailed metrics and insights.
- **AI-Powered Chat**: Conversational interface for research, powered by multiple specialized AI agents.
- **Research Tools**: Upload and analyze documents, get comprehensive investment insights.
- **Trending News**: Stay updated with the latest news relevant to companies and markets.
- **Threaded Conversations**: Persistent, context-aware chat threads for ongoing analysis.

---

## Architecture

- **Frontend** (`frontend/`):
  - Built with React, TypeScript, Vite, and Tailwind CSS
  - Modern, clean UI with support for chat, company pages, and research tools
  - Integrates with backend APIs for chat, company data, and file uploads

- **Backend** (`backend/`):
  - FastAPI web server exposing RESTful APIs for chat, companies, news, finance, research, and more
  - Multi-agent framework: Specialized AI agents (Finance, Market, Team, Risk, etc.) coordinated by a central MCP Orchestrator
  - Integrates with MongoDB (for chat, user data) and vector databases (for semantic search)
  - Connects to external AI (OpenAI, Perplexity) for advanced reasoning and real-time data

---

## How It Works

1. **User interacts via the frontend** (search, chat, research)
2. **Frontend calls backend APIs** for data, chat, and analysis
3. **Backend MCP Orchestrator** routes requests to specialized AI agents and data sources
4. **Agents analyze, reason, and respond** using internal knowledge and external AI
5. **Results are returned to the frontend** for display in a modern, user-friendly interface

---

## Getting Started

- See `frontend/README.md` for running the web app
- See `backend/README.md` for backend setup and architecture details

---

## Project Structure

- `frontend/` – React web application
- `backend/` – FastAPI backend with agentic AI framework

---

Intersectx aims to revolutionize investment research by combining multi-agent AI, real-time data, and a seamless user experience. 