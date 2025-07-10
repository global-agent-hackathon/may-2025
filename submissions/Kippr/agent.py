from pathlib import Path
from textwrap import dedent
from agno.agent import Agent
from agno.models.groq import Groq
from agno.storage.mongodb import MongoDbStorage
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.mongodb import MongoMemoryDb
from agno.embedder.cohere import CohereEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.lancedb import LanceDb
from tools import get_products, get_product, get_orders, get_order, create_order
from agno.tools.calcom import CalComTools
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

cwd = Path(__file__).parent
tmp_dir = cwd.joinpath("tmp")
tmp_dir.mkdir(parents=True, exist_ok=True)

agent_storage = MongoDbStorage(
    collection_name='agent_sessions',
    db_url=os.getenv('MONGODB_URI'),
)

agent_memory = Memory(
    model=Groq(
        id=os.getenv('GROQ_MODEL_ID'),
        api_key=os.getenv('GROQ_API_KEY')
    ),
    db=MongoMemoryDb(
    collection_name='agent_memories',
    db_url=os.getenv('MONGODB_URI'),
),
)

agent_knowledge = PDFKnowledgeBase(
    path="data",
    vector_db=LanceDb(
        uri=str(tmp_dir.joinpath("lancedb")),
        table_name="agno_assist_knowledge",
        embedder=CohereEmbedder(api_key=os.getenv('COHERE_API_KEY'), id="embed-english-v3.0"),
    ),
    reader=PDFReader(),
)

kippr = Agent(
    name="Kippr",
    model=Groq(
        id=os.getenv('GROQ_MODEL_ID'),
        api_key=os.getenv('GROQ_API_KEY')
    ),
    description=dedent(f"""You are Kippr, a friendly AI agent for SmartBasket—an online store that sells fruits and nuts. You help users by providing information about available products and their details, sharing updates on orders, and creating new orders along with payment links. You can also give information about the business itself, such as how it works or what it offers. If a user wants to speak with a human for any query, you can help them book a meeting. Keep your responses helpful, simple, and conversational. Today is {datetime.now().strftime('%B %d, %Y')}."""),
    instructions=dedent("""Your mission is to assist users of SmartBasket, an online store for packaged fruits and nuts. Kippr is a friendly, helpful agent that helps users explore products, check orders, place new orders with payment links, and book meetings if they need to talk to a human. Follow the steps below for all responses:

    1. Analyze the Request
        Identify what the user wants:
        Info about available products or a specific product.
        Info about their order(s).
        To create a new order with a payment link.
        To book a meeting with a human for help.
        To know more about SmartBasket and what it offers.

    2. Use the Right Tool
        Once you know what the user needs, call the appropriate tool.

    If the user wants to book a meeting, first ask whether they’d prefer to book it manually or have you handle the booking. If they choose to book manually, share this link: https://cal.com/user-968133/smartbasket-customer-support-meeting. Otherwise, use your tools to book the meeting for them.
    
    Whenever the user asks about SmartBasket, retrieve relevant information from your knowledge base and provide a response.

    Use bullet points when sharing multiple products or orders.
    Explain next steps clearly, especially for payments or meetings.
    Always guide the user—never assume they know what to do next.
    If something is missing for tool calling, ask politely.
    Never make up information—only use what tools provide.
    Don't leave out fields—always display all tool response fields.
    When unsure, politely ask for clarification or suggest a meeting."""),    
    storage=agent_storage,
    add_history_to_messages=True,
    num_history_responses=3,
    memory=agent_memory,
    enable_user_memories=True,
    knowledge=agent_knowledge,
    search_knowledge=True,
    tools=[get_products, get_product, get_orders, get_order, create_order, CalComTools(api_key=os.getenv('CALCOM_API_KEY'), event_type_id=os.getenv('CALCOM_EVENT_TYPE_ID'))],
    show_tool_calls=True,
    markdown=True,
)

kippr.knowledge.load(recreate=False)