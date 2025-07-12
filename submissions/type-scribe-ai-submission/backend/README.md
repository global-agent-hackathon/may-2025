# Type-Scribe AI: Backend

This repository contains the FastAPI backend application for **Type-Scribe AI**. It acts as the orchestrator for the AI agents that generate TypeScript SDKs from API documentation. This backend handles API requests from the frontend, manages the multi-agent workflow using `Agno`, integrates with `Graphlit` for documentation processing, and leverages Google Gemini for AI capabilities.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Navigate to the `type-scribe-ai` directory](#2-navigate-to-the-type-scribe-ai-directory)
  - [3. Create and Activate a Virtual Environment](#3-create-and-activate-a-virtual-environment)
  - [4. Install Dependencies](#4-install-dependencies)
  - [5. Environment Configuration](#5-environment-configuration)
  - [6. Run the FastAPI Application](#6-run-the-fastapi-application)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Project Structure](#project-structure)


## Features

*   **SDK Generation Orchestration**: Manages the end-to-end process of generating TypeScript SDKs.
*   **Multi-Agent System**: Utilizes `Agno` to orchestrate specialized AI agents for documentation understanding and SDK code generation.
*   **Documentation Ingestion**: Integrates with `Graphlit` to process and extract information from various API documentation formats (URLs or uploaded files).
*   **API Understanding**: AI agents powered by Google Gemini analyze text-based documentation to identify API endpoints, methods, parameters, and data structures.
*   **TypeScript SDK Code Generation**: AI agents generate well-structured and type-safe TypeScript code for the SDK, including client methods and type definitions.
*   **Usage Example Generation**: Provides a code example demonstrating how to use the newly generated SDK.
*   **CORS Configuration**: Securely handles cross-origin requests from the frontend.

## Technologies Used

This backend application is built using:

*   **Python 3.9+**: The core programming language.
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **Agno**: The AI agent framework used for orchestrating the multi-agent workflow.
*   **Graphlit**: A platform for ingesting, indexing, and querying unstructured content, used here for API documentation analysis.
*   **Google Gemini**: Large Language Model (LLM) for understanding API schemas and generating code.
*   **Pydantic**: Data validation and settings management using Python type hints.
*   **`python-dotenv`**: For loading environment variables from `.env` files.

## Architecture Overview

The backend serves as the central hub for the Type-Scribe AI system. It receives SDK generation requests from the frontend, then orchestrates a series of steps:

1.  **Documentation Ingestion**: Uses `Graphlit` to convert raw API documentation (URL or file) into a structured, queryable format.
2.  **API Understanding Agent**: An `Agno`-orchestrated agent, powered by Google Gemini, analyzes the Graphlit-processed documentation to extract a structured schema of the API (endpoints, methods, parameters, types).
3.  **SDK Generation Agent**: Another `Agno`-orchestrated agent, also using Google Gemini, takes the structured API schema and translates it into complete TypeScript SDK code, including type definitions and client methods.
4.  **Response**: The generated SDK code and a usage example are returned to the frontend.

## Prerequisites

Before running this backend application, ensure you have the following installed:

*   **Python**: Version 3.9 or higher.
*   **`pip`**: Python package installer (usually comes with Python).

## Getting Started

Follow these steps to set up and run the backend application locally:

### 1. Clone the repository

```bash
git clone https://github.com/808vita/type-scribe-ai
```
### 2. Navigate to the `type-scribe-ai` directory
```bash
cd type-scribe-ai
```
### 3. Create and Activate a Virtual Environment
It's highly recommended to use a Python virtual environment to manage dependencies.

On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```
### 4. Install Dependencies
Install all required Python packages using pip:
```bash
pip install -r requirements.txt
```
### 5. Environment Configuration
Create a `.env` file in the root of the `type-scribe-ai` directory. This file will store your API keys and credentials.

Copy the contents of `.env.example` into your new `.env` file and replace the placeholder values:

```env
# .env
# Graphlit API Credentials
# Get these from your Graphlit Developer Portal (https://portal.graphlit.dev/)
GRAPHLIT_ORGANIZATION_ID=YOUR_GRAPHLIT_ORGANIZATION_ID
GRAPHLIT_ENVIRONMENT_ID=YOUR_GRAPHLIT_ENVIRONMENT_ID
GRAPHLIT_JWT_SECRET=YOUR_GRAPHLIT_JWT_SECRET

# Google Gemini API Key (for Agno Agents)
# Get this from Google AI Studio or Google Cloud Console
GOOGLE_API_KEY=YOUR_GOOGLE_AI_API_KEY
```
*   `GRAPHLIT_ORGANIZATION_ID`: Your Graphlit Organization ID.
*   `GRAPHLIT_ENVIRONMENT_ID`: Your Graphlit Environment ID.
*   `GRAPHLIT_JWT_SECRET`: Your Graphlit JWT Secret.
    (You can obtain these from the Graphlit Developer Portal)
*   `GOOGLE_API_KEY`: Your Google Gemini API Key.
    (You can obtain this from Google AI Studio or the Google Cloud Console).

### 6. Run the FastAPI Application
Once all dependencies are installed and environment variables are set, you can start the FastAPI application:
```bash
fastapi dev app/main.py --port 8000
```
The server will typically run on `http://localhost:8000`. You can test the API by visiting `http://localhost:8000/docs` in your browser to see the interactive OpenAPI documentation (Swagger UI).

## API Endpoints
The main endpoint for SDK generation is:

*   `POST /generate-sdk`: Accepts API documentation (URL or file) and SDK configuration to generate a TypeScript SDK.

## Deployment
This backend can be easily deployed to container platforms like Google Cloud Run, AWS Fargate, or Docker Swarm. A `Dockerfile` is provided for containerization:

```dockerfile
# Use a slim Buster-based Python image as the base
FROM python:alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the /app/app directory
COPY ./app /app/app

# Expose the port on which the FastAPI application will listen
EXPOSE 8000

# Command to run the application using FastAPI's built-in server
CMD [ "fastapi","run","app/main.py","--port","8000" ]
```
Ensure your `GRAPHLIT_ORGANIZATION_ID`, `GRAPHLIT_ENVIRONMENT_ID`, `GRAPHLIT_JWT_SECRET`, and `GOOGLE_API_KEY` are configured as environment variables in your deployment environment.

## Project Structure
*   `app/main.py`: The main FastAPI application file, containing routes, logic, and agent orchestration.
*   `app/__init__.py`: Initializes the Python package.
*   `requirements.txt`: Lists all Python dependencies.
*   `.env.example`: Template for environment variables.
*   `Dockerfile`: Defines the Docker image for containerization.
*   `activate instructions.txt`: Basic instructions for virtual environment activation and running.
