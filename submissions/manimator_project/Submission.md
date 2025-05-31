---
name: Hackathon Project Submission
about: Submit your project for the Global Agent Hackathon
title: "[Project Submission] Manimator: AI-Powered Manim Animations"
labels: submission
assignees: ''

---

# Project Title
Manimator: AI-Powered Manim Animations

## Overview of the Idea
Manimator is an AI-powered tool that automates the creation of animations using the Manim library. Manim, famously used by 3Blue1Brown, is a powerful Python library for generating precise mathematical animations. Manimator simplifies this process by allowing users to describe their desired animation in natural language, which an AI agent then translates into Manim code and renders into a video. This addresses the complexity and learning curve often associated with using Manim directly, making animation creation accessible to a broader audience, including educators, content creators, and students.

## Project Goal
The primary goal of Manimator is to democratize Manim animation creation. We aim to:
- Enable users to generate Manim animations through simple natural language prompts.
- Provide an iterative workflow where users can refine animations by providing feedback on AI-generated code.
- Reduce the time and effort required to produce high-quality mathematical and educational animations.
- Showcase the power of agentic AI in a creative and educational context.

## How It Works
Manimator utilizes a multi-agent system in the backend and a user-friendly web interface in the frontend.

- **User Flow**:
    1.  The user visits the Manimator web application.
    2.  On the landing page, they can enter a natural language prompt describing the animation they want to create (e.g., "Show a circle transforming into a square, then a triangle").
    3.  This prompt initiates a chat session. The user's prompt is sent to the backend.
    4.  The backend AI agents process the prompt:
        *   An `Animation Decomposer Agent` breaks down the user's request into detailed, actionable steps or "scenes" suitable for Manim. This agent utilizes tools to search Manim documentation (potentially sourced using Firecrawl) and a curated dataset of Manim code examples (embeddings for RAG possibly generated via Together AI) to better understand the user's intent and map it to Manim capabilities.
        *   A `Manim Code Agent` takes these decomposed steps and generates the corresponding Python code for Manim. This agent also leverages tools to access comprehensive Manim documentation and the curated dataset of code examples (from `Noxus09/manim-dataset` on Hugging Face, with RAG powered by embeddings, potentially from Together AI) to ensure accuracy and best practices.
    5.  The generated Manim code is then executed by the backend, which attempts to render a video.
    6.  If the code executes successfully, the rendered video and the Manim code are displayed to the user in the chat interface.
    7.  If there are errors during rendering:
        *   A `Debugger Agent` attempts to fix the errors in the Manim Code. It also uses the Manim documentation and curated code example dataset (enhanced by RAG with embeddings, potentially from Together AI) to find solutions and retries rendering. This process can iterate a few times.
    8.  The user can then:
        *   View the generated video.
        *   Inspect the Manim code.
        *   Provide further natural language instructions to modify the animation (e.g., "Make the circle blue", "Slow down the transformation").
    9.  These update requests are processed by an `Updater Agent` which modifies the existing Manim code based on the user's feedback. The animation is then re-rendered.
    10. The user can iterate on their animation, view different generated video variants, and download the final video.

- **Core Functionality**:
    -   **Natural Language to Manim Code**: Converts user prompts into runnable Manim Python scripts.
    -   **AI-Powered Code Generation & Debugging**: Agents, built with Agno, leverage Manim documentation (potentially sourced via Firecrawl) and a curated dataset of code examples (from `Noxus09/manim-dataset` on Hugging Face, with RAG enhanced by embeddings from services like Together AI) for accurate code generation and error correction.
    -   **Automated Video Rendering**: Executes the generated Manim code to produce an MP4 video.
    -   **Iterative Refinement**: Allows users to modify and improve animations through follow-up prompts.
    -   **Error Handling & Debugging**: AI agents attempt to automatically debug and correct errors in the generated Manim code.
    -   **Code Display**: Shows the generated Manim code to the user for transparency and learning.
    -   **Video Preview & Variants**: Users can preview the generated video and switch between different animation variants produced during the iterative process.

- **Multimodal Elements**:
    -   **Text**: User input (prompts, modification requests), AI agent responses, Manim code display.
    -   **Video**: Output of the Manim animation rendering.
    -   **Images**: The frontend uses images/icons for UI elements (e.g., `landing_page.png`, `chat_page.png` are mockups/visuals).

## Tools Used
-   **Backend**:
    -   Python
    -   FastAPI (for creating the web server and API endpoints)
    -   Manim (the core animation engine)
    -   Agno (Python framework used for developing the AI agents: `animation_decomposer_agent`, `manim_agent`, `debugger_agent`, `updater_agent`)
        -   Currently uses `Gemini` as the LLM for the agents. A custom fine-tuned model, `Noxus09/qwen-3-4b-manim-finetuned` (Qwen-3 4B fine-tuned on Manim code), is also available on Hugging Face and represents a specialized alternative for enhanced performance on Manim-specific tasks.
    -   `animation_decomposer_agent`: Custom agent (built with Agno) to break down animation requests.
    -   `manim_agent`: Custom agent (built with Agno) to generate Manim code.
    -   `debugger_agent`: Custom agent (built with Agno) to debug Manim code.
    -   `updater_agent`: Custom agent (built with Agno) to update existing Manim code.
    -   Tools for agents:
        -   `get_manim_docs`: Tool to fetch Manim documentation.
        -   `get_code_example`: Tool to retrieve Manim code examples, leveraging a RAG approach. This involves:
            - A curated dataset (`Noxus09/manim-dataset` on Hugging Face) of Manim code snippets and corresponding prompts.
            - Embeddings for this dataset and user queries, potentially generated using services like Together AI.
            - Firecrawl may be used to gather or keep updated the corpus of Manim examples/documentation that feeds into the RAG system.
    -   Standard Python libraries (os, tempfile, shutil, subprocess, logging).
-   **Frontend**:
    -   TypeScript
    -   React
    -   Vite (build tool)
    -   Tailwind CSS (styling, via shadcn/ui)
    -   `shadcn/ui` (component library)
    -   `lucide-react` (icons)
    -   `react-router-dom` (routing)
    -   `uuid` (for generating unique session IDs)
-   **Development & Version Control**:
    -   Git & GitHub
    -   VS Code
    -   `uv` (Python package manager)
    -   `.python-version` (pyenv)
    -   `dotenv` for environment variable management.

## UI Approach
The user interface is a web application with two main pages:
1.  **Landing Page (`LandingPage.tsx`)**:
    *   Features a prominent input field for users to type their initial animation prompt.
    *   May include example prompts or suggestions.
    *   Provides options to sign in/sign up.
    *   Showcases "My Projects" and "From the Community" sections, suggesting features for user accounts and community sharing.
    *   The design is modern and clean, utilizing components from `shadcn/ui`.
    *   Visuals for this are in `landing_page.png`.

2.  **Chat Page (`ChatPage.tsx`, `SideChatBar.tsx`, `VideoCanvas.tsx`)**:
    *   This is where the primary interaction happens after the initial prompt.
    *   A chat-like interface (`SideChatBar.tsx`) where users can type further instructions or modifications. The history of prompts and AI responses (including generated code snippets or error messages) would be displayed here.
    *   A video preview area (`VideoCanvas.tsx`) to display the rendered Manim animation.
    *   This area also shows thumbnails or a list of previously generated video variants, allowing the user to switch between them.
    - The Manim code generated by the AI is also displayed, likely in the chat sidebar or a dedicated panel.
    *   Visuals for this are in `chat_page.png`.

The UI aims to be intuitive, guiding the user through the process of creating and refining their animation with clear visual feedback.

## Visuals
- `landing_page.png` (mockup of the landing page)
- `chat_page.png` (mockup of the main chat/animation interface)

*(These images were provided and represent the visual concept of the application.)*

## Team Information
- **Team Lead**: [krishnarathore12] - [AI Engineer]
- **Team Members**: [Edward4762] - [Full Stack Developer], [deb-cmd] - [UX Designer] 
- **Background/Experience**: We are a team passionate about AI, software development, and education. We believe in the power of tools like Manim to make complex topics more accessible and engaging, and we are excited to apply agentic AI to streamline the animation creation process. 

## Prize Category (leave blank, to be assigned by judges)
- [ ] Best use of Agno
- [ ] Best use of Firecrawl
- [ ] Best use of Mem0
- [ ] Best use of Graphlit
- [ ] Best use of Browser Use
- [ ] Best use of Potpie
- [ ] Best Overall Project

## Demo Video Link
https://drive.google.com/file/d/1FQyMsJNEdDRVfbGZzvEJywm90udz4g6k/view?usp=sharing

## Additional Notes
Manimator leverages multiple AI agents, built using the Agno framework, each specialized for a part of the animation generation pipeline: decomposing user requests, writing initial Manim code, debugging errors, and applying user-requested updates. This modular agentic design, combined with tools that allow agents to search official Manim documentation and a curated dataset of Manim code examples (`Noxus09/manim-dataset` on Hugging Face [https://huggingface.co/datasets/Noxus09/manim-dataset](https://huggingface.co/datasets/Noxus09/manim-dataset)), allows for more robust and targeted AI assistance throughout the creative process. The RAG (Retrieval Augmented Generation) capabilities for accessing code examples are enhanced by embeddings (potentially from Together AI), and the knowledge base for RAG may be populated or updated using Firecrawl for web data extraction.

Furthermore, a specialized language model, `qwen-3-4b-manim-finetuned`, has been fine-tuned specifically on Manim code and is available on Hugging Face ([https://huggingface.co/Noxus09/qwen-3-4b-manim-finetuned](https://huggingface.co/Noxus09/qwen-3-4b-manim-finetuned)). While the current live version utilizes a general-purpose model, this fine-tuned model offers a pathway for future enhancements to Manimator's code generation quality and understanding of Manim-specific nuances.

The project also emphasizes providing transparency to the user by showing the generated Manim code, which can serve as a learning tool for those interested in Manim development.
The backend is built with FastAPI, ensuring a scalable and efficient API, while the frontend uses React and TypeScript for a modern, responsive user experience.
We are excited about the potential of Manimator to empower creators and educators.