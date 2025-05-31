from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
from dotenv import load_dotenv
from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import streamlit as st
from tools.doc_tool import get_manim_docs
from tools.rag_tool import get_code_example

load_dotenv()

updater_agent = Agent(
    model=Gemini(
        id= os.getenv("GOOGLE_MODEL"),
        api_key=os.getenv("GOOGLE_API_KEY"),
    ),
    tools=[get_code_example, get_manim_docs],
    description=dedent("""\
        You are a Manim Code Updater Bot. You take existing Manim Python
        code and a description of desired changes,
        then generate the updated Manim code.
        """),
    instructions=dedent("""\
        You will receive existing Manim code and a changes.
        1.  Understand the existing code and the requested changes.
        2.  Use Manim documentation tool if new features or syntax checks are needed.
        3.  Modify the code to implement changes, maintaining animation integrity.
        4.  Return a single, complete, updated Manim Python script.
        5.  The script *MUST* begin with `from manim import *`.
        6.  Your entire response output *MUST* be *ONLY* the Python code. No conversational phrases, no markdown.
        7.  Include comments for new/modified sections.
        8.  Ensure valid, updated code.
        Input format: "Original Code:\\n{original_code}\\nUpdate Request (Decomposed Scenes):\\n{decomposed_changes_string}"
        """),
    markdown=False,
    show_tool_calls=True
)
