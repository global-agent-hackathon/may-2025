import datetime
import requests
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
import json
from utils.config import config
from routes.agentRoutes import router as agent_router
from routes.stockRoutes import router as stock_router
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()
GROQ_API_KEY = config.GROQ_API_KEY
GEMINI_API_KEY = config.GEMINI_API_KEY
EXA_API_KEY = config.EXA_API_KEY
NEWS_API_KEY = config.NEWS_API_KEY
REDIS_URL = config.REDIS_URL

def get_router_paths(router):
    return [route.path for route in router.routes if hasattr(route, 'path')]

@router.get("/health", response_class=HTMLResponse)
async def health_check(request: Request):
    """Health check endpoint to verify the API server status and connections."""
    try:
        agent_paths = get_router_paths(agent_router)
        stock_paths = get_router_paths(stock_router)
        all_paths = sorted(set(agent_paths + stock_paths))
        response_data = {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "uptime": "OK",
            "api": {
                "groq_api": {
                    "status": "connected" if GROQ_API_KEY else "not configured",
                    "icon": "🟢" if GROQ_API_KEY else "🔴"
                },
                "gemini_api": {
                    "status": "connected" if GEMINI_API_KEY else "not configured",
                    "icon": "🟢" if GEMINI_API_KEY else "🔴"
                },
                "exa_api": {
                    "status": "connected" if EXA_API_KEY else "not configured",
                    "icon": "🟢" if EXA_API_KEY else "🔴"
                },
                "news_api": {
                    "status": "connected" if NEWS_API_KEY else "not configured",
                    "icon": "🟢" if NEWS_API_KEY else "🔴"
                },
                "redis_url": {
                    "status": "connected" if REDIS_URL else "not configured",
                    "icon": "🟢" if REDIS_URL else "🔴"
                }
            },
            "ip": requests.get('https://api.ipify.org').text,
            "services": all_paths,
        }        
            
        return JSONResponse(content=response_data)

    except Exception as e:
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "error": str(e)
        }
        
        return JSONResponse(content=error_response)