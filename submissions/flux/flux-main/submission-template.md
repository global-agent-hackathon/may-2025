---
name: Hackathon Project Submission
about: Submit your project for the Global Agent Hackathon
title: "[Project Submission] Flux: Superintelligent Form Builder with Agents and Memory"
labels: submission
assignees: ''
---

# Project Title
Flux: Form Builder with AI-Powered Creation and Analysis

## Overview of the Idea
Flux simplifies form creation and response analysis through AI. Users create a project with a description, and Flux builds contextually relevant forms based on natural language requests. Beyond storage, Flux allows users to analyze response data through conversation, generating insights and visualizations on demand. Additionally, Flux scrapes URLs and analyzes attachments in responses to provide richer insights. We've integrated Agno for reasoning, Mem0 for contextual memory across the form lifecycle, and Firecrawl for content analysis to power this intelligence layer.

## Project Goal
Create a tool that reduces friction in form creation and unlocks deeper insights from form data through conversational queries and external content analysis.

## How It Works
- User signs in with Clerk
- Creates a project/workspace with description
- Clicks "New Form" and enters a goal like: "Create a product feedback form with rating scales"
- Agno interprets the request using project context and past form creation patterns from Mem0
- Menu buttons and command interface let you control structure and behavior
- Chat button opens interface for editing, analysis, or help
- Firecrawl scrapes external links (e.g., portfolios, websites) and analyzes attachments from responses
- Mem0 stores past form structures, modifications, and insights from submissions
- Once responses arrive, users query their data:
  - "What's the average satisfaction rating?"
  - "Generate a pie chart of feature priorities"
  - "Summarize themes in negative feedback"
  - "Show sentiment trends over time"
  - "Analyze the common elements in submitted portfolios"
  - "How does this compare to last month's feedback?"

## Tools Used
- Agno – Agentic reasoning layer for form building and analysis
- Mem0 – Project memory for context retention across form creation and analysis
- Gemini API – Core LLM
- Firecrawl – Scraping external URLs and analyzing attachments
- Next.js 14 – Fullstack app
- Tailwind CSS + Shadcn UI – UI system
- Bun – Runtime
- Zustand – State management
- TanStack Query/Table – Data syncing & display
- React Hook Form + Zod – Validation
- NeonDB + Prisma – DB layer
- Clerk – Auth

## Use Cases
### 1. Product Feedback Forms
- Create comprehensive feedback forms quickly
- Query sentiment patterns in responses
- Visualize feature requests and priorities
- Analyze trends in customer satisfaction
- Extract insights from attached screenshots or documentation

### 2. Hiring Forms
- Build application forms with natural language
- Identify top candidates through response analysis
- Visualize applicant distribution by skills
- Extract insights from GitHub, portfolios, and attached resumes
- Auto-evaluate technical expertise based on submitted URLs

### 3. Event Registration
- Create event registration forms efficiently
- Understand attendee demographics through queries
- Generate visualizations of registration patterns
- Analyze feedback for future planning
- Extract data from submitted social profiles or company websites

### 4. Course/Workshop Applications
- Build application forms quickly
- Understand applicant goals and backgrounds
- Visualize applicant distribution by interests
- Analyze application quality and fit
- Review attached work samples or project documentation

## UI Approach
- Clean layout with sidebar
- Intuitive menu button interface
- AI chat button for assistance
- Table view with filters
- Interactive visualizations
- Fully responsive

## Visuals
- Builder UI
- Chat interface
- Visualization dashboard
- Response analysis view
- Scraped content insights

## Team Info
Team Lead: Sarthak Jain @srthkdev  
Background/Experience: Fullstack and AI workflow developer with experience in building productivity-first LLM tools.

## Prize Category
- Best Overall Project
- Best use of Agno
- Best use of Firecrawl
- Best use of Mem0

## Demo Video Link
To be added before deadline

## Final Notes
Forms are still built with outdated workflows and yield limited insights. Flux addresses these problems through three key components:
1. Form creation through natural language using Agno's reasoning capabilities and Mem0's project context
2. Contextually-aware forms that understand the project's goals through Mem0's memory system
3. Rich data analysis through conversation with historical context from Mem0
4. Enhanced insights from external content via Firecrawl

This combination saves time and uncovers valuable insights that would otherwise require manual analysis. Flux remembers project context, past form structures, and submission patterns, making each new form more relevant and each analysis more insightful.