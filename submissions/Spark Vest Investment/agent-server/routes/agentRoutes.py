import os
import datetime
import json
import requests
import groq
from fastapi import FastAPI, APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from agno.agent import RunResponse
from controllers.agents import multi_ai
import dotenv
from utils.config import config
router = APIRouter()

dotenv.load_dotenv()
templates = Jinja2Templates(directory="templates")

GROQ_API_KEY = config.GROQ_API_KEY
GEMINI_API_KEY = config.GEMINI_API_KEY

groq_client = groq.Client(api_key=GROQ_API_KEY)

@router.get("/chat", response_class=HTMLResponse)
def chat(request: Request, query: str = None):
    """
    API endpoint to handle user investment-related questions and return AI-generated insights.
    """
    # Check if request is from a browser or format is explicitly set to html
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        current_year = datetime.datetime.now().year
        example_response = {
            "question": "What are good tech stocks to invest in?",
            "answer": "Some popular tech stocks to consider include Apple (AAPL), Microsoft (MSFT), Google (GOOGL), and Amazon (AMZN). However, you should always do your own research and consider your investment goals and risk tolerance before investing."
        }
        
        return templates.TemplateResponse(
            "route.html",
            {
                "request": request,
                "route_path": "/chat",
                "method": "GET",
                "full_path": str(request.url).split("?")[0],
                "description": "Chat endpoint that uses Groq's LLaMa model to answer investment questions.",
                "parameters": [
                    {"name": "query", "type": "string", "description": "The investment question to ask"},
                    {"name": "format", "type": "string", "description": "Response format (html or json)"}
                ],
                "example_query": "What are good tech stocks to invest in?",
                "example_response": json.dumps(example_response, indent=2),
                "current_year": current_year
            }
        )
    
    # Handle regular API calls
    if not query:
        return JSONResponse(content={"error": "Query parameter is required"})
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role": "system", "content": "You are an AI investment assistant."},
                      {"role": "user", "content": query}]
        )
        
        answer = response.choices[0].message.content
        return JSONResponse(content={"question": query, "answer": answer})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@router.get("/agent", response_class=HTMLResponse)
def ask(request: Request, query: str = None):
    """
    API endpoint to handle user investment-related questions and return AI-generated insights.
    """
    # Check if request is from a browser or format is explicitly set to html
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        current_year = datetime.datetime.now().year
        example_response = {
            "question": "Should I invest in index funds?",
            "answer": "Index funds are often a good choice for passive investors looking for broad market exposure with low fees. They offer diversification and typically outperform actively managed funds in the long term. However, the suitability depends on your investment goals, time horizon, and risk tolerance."
        }
        
        return templates.TemplateResponse(
            "route.html",
            {
                "request": request,
                "route_path": "/agent",
                "method": "GET",
                "full_path": str(request.url).split("?")[0],
                "description": "Agent endpoint that uses a multi-AI system to provide sophisticated investment advice.",
                "parameters": [
                    {"name": "query", "type": "string", "description": "The investment question to ask"},
                    {"name": "format", "type": "string", "description": "Response format (html or json)"}
                ],
                "example_query": "Should I invest in index funds?",
                "example_response": json.dumps(example_response, indent=2),
                "current_year": current_year
            }
        )
    
    # Handle regular API calls
    if not query:
        return JSONResponse(content={"error": "Query parameter is required"})
    
    try:
        response: RunResponse = multi_ai.run(query)
        answer = response.content

        return JSONResponse(content={"question": query, "answer": answer})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)})