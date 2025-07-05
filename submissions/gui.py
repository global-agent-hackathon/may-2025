from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.embedder.google import GeminiEmbedder
from agno.models.google.gemini import Gemini
from src.speech.speech_to_text import STT
from src.speech.text_to_speech import TTS
from agno.memory.v2.memory import Memory
from dotenv import load_dotenv
from src.agent import Agent
from ui import launch_ui
from groq import Groq
import os

load_dotenv()
google_key = os.getenv('GOOGLE_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

model=Gemini(id='gemini-2.0-flash',api_key=google_key,temperature=0.3)
embedder=GeminiEmbedder(id='models/embedding-001',api_key=google_key)
memory=Memory(model=model,db=SqliteMemoryDb(table_name="memories", db_file='./database/memories.db'))
client=Groq(api_key=groq_api_key)

agent=Agent(model=model,memory=memory,embedder=embedder)
tts=TTS(client=client)
stt=STT(client=client)

launch_ui(agent=agent,tts=tts,stt=stt)