from agno.tools.crawl4ai import Crawl4aiTools
from agno.memory.v2.memory import Memory
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.url import UrlKnowledge
from agno.vectordb.chroma import ChromaDb
from agno.agent import Agent as AgnoAgent
from agno.embedder.base import Embedder
from uiautomation import GetScreenSize
from agno.models.base import Model
from src.tools import WindowsTools
from getpass import getuser
from textwrap import dedent
from pathlib import Path
import platform

class Agent:
    def __init__(self,model:Model,embedder:Embedder=None,memory:Memory=None):
        self.model=model
        self.embedder=embedder
        self.memory=memory
        self.tools=[WindowsTools(),Crawl4aiTools()]
        if self.embedder is not None:
            self.vector_db=ChromaDb(collection='KnowledgeBase',path='./database/knowledgebase',persistent_client=True,embedder=self.embedder)
        self.knowledge_base=None

    def load_system_prompt(self):
        with open('./src/prompt/system.md') as f:
            system_message=dedent(f.read())
        width, height = GetScreenSize()
        parameters={
            'os':platform.system(),
            'home_dir':Path.home().as_posix(),
            'user':getuser(),
            'resolution':f'{width}x{height}'
        }
        return system_message.format(**parameters)

    def add_pdf_knowledge(self,file_path):
        self.knowledge_base=PDFKnowledgeBase(path=file_path,vector_db=self.vector_db)
        self.knowledge_base.load()

    def add_url_knowledge(self,url):
        self.knowledge_base=UrlKnowledge(urls=[url],vector_db=self.vector_db)
        self.knowledge_base.load()

    def invoke(self,query:str):
        agent=AgnoAgent(name='Windows-Use',model=self.model,memory=self.memory,system_message=self.load_system_prompt(),
        tools=self.tools,knowledge=self.knowledge_base,enable_agentic_memory=True,search_knowledge=True,
        add_history_to_messages=True,enable_user_memories=True,markdown=True)
        response=agent.run(query)
        return response
    
    def print_response(self,query:str):
        agent=AgnoAgent(name='Windows-Use',model=self.model,memory=self.memory,system_message=self.load_system_prompt(),
        tools=self.tools,knowledge=self.knowledge_base,enable_agentic_memory=True,search_knowledge=True,show_tool_calls=False,
        add_history_to_messages=True,enable_user_memories=True,markdown=True)
        agent.print_response(query,stream=True)