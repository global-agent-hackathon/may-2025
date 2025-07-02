import groq
import os
from dotenv import load_dotenv

# AI assistant imports
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.yfinance import YFinanceTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.agent import Agent, RunResponse
from agno.tools.exa import ExaTools
from utils.config import config

GROQ_API_KEY = config.GROQ_API_KEY
EXA_API_KEY = config.EXA_API_KEY
    
web_search_agent = Agent(
    name="web_agent",
    role="search the web for information based on the user given input",
    model=Groq(id="deepseek-r1-distill-llama-70b", api_key=GROQ_API_KEY),
    tools=[
        DuckDuckGoTools(search=True, news=True),
    ],
    instructions=[
        "You are a very professional web search AI agent",
        "your job is to search the web for information based on the user given input",
        "provide exact information to the user available on the web",
    ],
)

financial_agent = Agent(
    name="financial_agent",
    role="get financial information",
    model=Groq(id="deepseek-r1-distill-llama-70b", api_key=GROQ_API_KEY),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            company_info=True,
            technical_indicators=True,
            historical_prices=True,
            key_financial_ratios=True,
            income_statements=True,
        ),
        ExaTools(
            api_key=EXA_API_KEY,
            include_domains=["investing.com", "finance.yahoo.com", "cnbc.com"],
            category="financial",
        ),
    ],
    instructions=[
        "You are a very professional financial advisor AI agent",
        "your job is to provide financial information to users",
        "you can provide stock price, analyst recommendations, and stock fundamentals",
        "you can also provide information about companies, industries, and financial terms",
    ],
)

multi_ai = Agent(
    team=[web_search_agent, financial_agent],
    model=Groq(id="deepseek-r1-distill-llama-70b", api_key=GROQ_API_KEY),
    markdown=True,
)
