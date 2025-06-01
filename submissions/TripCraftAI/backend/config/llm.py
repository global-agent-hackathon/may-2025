from agno.models.google import Gemini
from agno.models.openai import OpenAIChat

model = Gemini(id="gemini-2.0-flash-001", temperature=0.1)
model2 = OpenAIChat(id="gpt-4o", temperature=0.1)
