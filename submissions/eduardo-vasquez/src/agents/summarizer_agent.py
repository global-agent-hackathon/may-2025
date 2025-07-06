"""Example: Meeting Summarizer & Visualizer Agent

This script uses OpenAITools (transcribe_audio, generate_image, generate_speech)
to process a meeting recording, summarize it, visualize it, and create an audio summary.

Requires: pip install openai agno
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from config import settings


instructions = dedent(
    """\
You are an AI summarizer. Summarize meeting transcripts to help teams align and take action.

Extract only explicitly stated details:

**Meeting Metadata**
- Title (as stated in the transcript)
- Date and time

**Attendees**
- Only list names and email addresses if both are clearly mentioned
- Do not infer or add missing people

**Meeting Summary**
- Use bullet points
- Only include facts and decisions stated in the text
- Maintain a professional tone

**Action Items**
- List only tasks explicitly assigned
- Each item must include:
  - Task title
  - Responsible person
  - Clear description of what they must do

Do not invent, infer, or assume anything not in the source text.
"""
)


description = dedent(
    """\
Extract meeting title, date, attendee names and emails, key discussion points, and assigned action items—only as explicitly stated in the transcript.
"""
)


summarizer_agent = Agent(
    name="Summarizer Agent",
    role="Summarize the text",
    model=OpenAIChat(id=settings.LLM_MODEL_NAME, api_key=settings.OPENAI_API_KEY),
    description=description,
    instructions=instructions,
    markdown=True,
    show_tool_calls=True,
)
