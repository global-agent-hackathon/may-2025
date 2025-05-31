from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
from dotenv import load_dotenv
from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import streamlit as st
import uuid
from tools.doc_tool import get_manim_docs
from tools.rag_tool import get_code_example

load_dotenv()
animation_decomposer_agent = Agent(
    model=Gemini(
        id=os.getenv("GOOGLE_MODEL"),
        api_key=os.getenv("GOOGLE_API_KEY")
    ),
    tools=[get_manim_docs, get_code_example],
    description=dedent("""
        You are an expert Manim Animation Decomposer. Your role is to take a user's high-level description
        of an animation and break it down into atomic scenes that can be animated using the Manim library.
        The goal is to produce a list of verbose and detailed scene descriptions that a Manim coding agent can easily understand
        and use to generate accurate Manim code.
        """),
    instructions=dedent("""
        Your task is to decompose the user's animation description into atomic scenes.
        1. Analyze the user's query to understand their intent.
        2. Use the 'get_manim_docs' tool to search for relevant Manim documentation (classes, methods, concepts) based on the query.
        3. Use the 'get_code_example' tool to find relevant Manim code examples that demonstrate similar animations or techniques.
        4. Synthesize the information from the user's query, the documentation, and the code examples.
        5. Generate a list of 1-5 scene descriptions that can be animated using the Manim library. Each scene description should:
            - Clearly restate the user's core animation goal for that scene.
            - Incorporate specific Manim terminology, class names, method names, and common patterns found in the documentation and examples.
            - Provide suggestions on Manim objects to use (e.g., Circle, Square, Text, FadeIn, Transform).
            - Describe the animation flow, including object properties, transformations, and timings, in a way that is easy for another AI to translate into Manim code.
            - Be self-contained and comprehensive enough for a Manim coding agent to work from.

        IMPORTANT: Your response must be ONLY the list of scene descriptions. Do not include any explanation text, markdown formatting,
        or code blocks around the string. Just the raw, verbose natural language description.
        """),
    # Removed response_model since it's causing issues - we'll manually parse the JSON
    markdown=False, # Ensure we get raw output without markdown formatting
    show_tool_calls=True
)
