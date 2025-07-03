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

debugger_agent = Agent(
    model=Gemini(
        id= os.getenv("GOOGLE_MODEL"),
        api_key=os.getenv("GOOGLE_API_KEY"),
        ),
    tools=[get_code_example, get_manim_docs],
    description=dedent("""\
        You are a Manim Debugging Bot. You analyze Manim Python code
        that produced an error, identify the cause, and provide a corrected version.
        Use Manim documentation if needed.
        """),
    instructions=dedent("""\
        You will receive Manim Python code and an error message.
        1.  Analyze the code and error.
        2.  Use the Manim documentation tool for Manim-specific errors.
        3.  Identify and fix the error(s).
        4.  Return a complete, corrected Manim Python script.
        5.  The script *MUST* begin with `from manim import *`.
        6.  Your entire response output *MUST* be *ONLY* the Python code. No conversational phrases, no markdown.
        7.  Ensure the corrected code is valid and addresses the reported error.
        Input format: "Code:\\n{faulty_code}\\nError:\\n{error_message}"
        """),
    markdown=False,
    show_tool_calls=True
)

