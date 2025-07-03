from fastapi import FastAPI, HTTPException, status, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

# Import the agent
from agents.superwizard_agent import get_superwizard_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate environment variables
def validate_environment():
    """Validate required environment variables."""
    required_vars = ["OPENROUTER_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == "your_openrouter_api_key_here":
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing or invalid environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all required variables are set")
        return False
    
    return True

# Validate environment on startup
if not validate_environment():
    logger.warning("Some environment variables are not properly configured. Server may not work correctly.")

class HealthCheck(BaseModel):
    """Response model for health check endpoint."""
    status: str = "OK"
    service: str = "Superwizard Server"
    version: str = "1.0.0"

class AgentRunRequest(BaseModel):
    """Request model for agent runs."""
    message: str
    user_id: str = "default-user"
    stream: bool = False

# Create the FastAPI app
app = FastAPI(
    title="Superwizard Server",
    description="AI-powered DOM automation server using Gemini 2.0 Flash",
    version="1.0.0",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create the agent with proper storage
superwizard_agent = get_superwizard_agent(debug_mode=False)

# Root endpoint
@app.get("/", 
         tags=["root"],
         summary="Root endpoint",
         response_description="Returns basic server information")
async def root() -> Dict[str, Any]:
    """
    Root endpoint that provides basic server information.
    """
    return {
        "message": "Superwizard Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "agents": "/v1/agents",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Health check endpoint
@app.get("/health",
         tags=["healthcheck"],
         summary="Perform a Health Check",
         response_description="Return HTTP Status Code 200 (OK)",
         status_code=status.HTTP_200_OK,
         response_model=HealthCheck)
async def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    
    Endpoint to perform a healthcheck on. This endpoint can primarily be used by
    Docker to ensure a robust container orchestration and management is in place.
    Other services which rely on proper functioning of the API service will not
    deploy if this endpoint returns any other HTTP status code except 200 (OK).
    
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(
        status="OK",
        service="Superwizard Server",
        version="1.0.0"
    )

# Status endpoint
@app.get("/status",
         tags=["status"],
         summary="Get detailed server status",
         response_description="Returns detailed server status information")
async def get_status() -> Dict[str, Any]:
    """
    Get detailed server status including database connectivity and agent information.
    """
    try:
        # Test database connection
        from db.session import db_engine
        from sqlalchemy import text
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "disconnected"
    
    return {
        "service": "Superwizard Server",
        "version": "1.0.0",
        "status": "running",
        "database": {
            "status": db_status
        },
        "agents": {
            "count": 1,
            "names": [superwizard_agent.name]
        },
        "environment": {
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "port": int(os.getenv("SERVER_PORT", "7777"))
        }
    }

# Agent endpoints
@app.get("/v1/agents",
         tags=["agents"],
         summary="List available agents")
async def list_agents() -> Dict[str, Any]:
    """List all available agents."""
    return {
        "agents": [
            {
                "name": superwizard_agent.name,
                "description": "AI-powered DOM automation agent",
                "available": True
            }
        ]
    }

# Health monitoring endpoint
@app.get("/v1/health/detailed",
         tags=["monitoring"],
         summary="Detailed health check with component status")
async def detailed_health() -> Dict[str, Any]:
    """Comprehensive health check of all system components."""
    health_status = {
        "status": "healthy",
        "timestamp": "now",
        "components": {}
    }
    
    # Check database
    try:
        from db.session import db_engine
        from sqlalchemy import text
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["components"]["database"] = {"status": "healthy", "latency": "low"}
    except Exception as e:
        health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check agent
    try:
        test_agent = get_superwizard_agent(debug_mode=False)
        health_status["components"]["agent"] = {"status": "healthy", "name": test_agent.name}
    except Exception as e:
        health_status["components"]["agent"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check environment
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key or openrouter_key == "your_openrouter_api_key_here":
        health_status["components"]["openrouter"] = {"status": "unhealthy", "error": "API key not configured"}
        health_status["status"] = "degraded"
    else:
        health_status["components"]["openrouter"] = {"status": "healthy", "configured": True}
    
    return health_status

# Legacy playground agents endpoint
@app.get("/v1/playground/agents",
         tags=["legacy"],
         summary="Legacy playground agents endpoint - redirected")
async def list_agents_legacy() -> Dict[str, Any]:
    """Legacy playground endpoint that redirects to the new agents endpoint."""
    return await list_agents()

# Legacy playground endpoint redirect
@app.post("/v1/playground/agents/{agent_name}/runs",
          tags=["legacy"],
          summary="Legacy playground endpoint - redirected")
async def run_agent_legacy(
    agent_name: str,
    message: str = Form(...),
    user_id: str = Form(default="default-user"),
    stream: str = Form(default="false")
) -> Dict[str, Any]:
    """
    Legacy playground endpoint that redirects to the new agent endpoint.
    """
    return await run_agent(agent_name, message, user_id, stream)

@app.post("/v1/agents/{agent_name}/runs",
          tags=["agents"],
          summary="Run an agent with a message")
async def run_agent(
    agent_name: str,
    message: str = Form(...),
    user_id: str = Form(default="default-user"),
    stream: str = Form(default="false")
) -> Dict[str, Any]:
    """
    Run an agent with the provided message.
    """
    if agent_name != "superwizard_dom_agent":
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found"
        )
    
    try:
        logger.info(f"Running agent with message: {message[:50]}...")
        
        # Create agent instance with user context
        user_agent = get_superwizard_agent(
            user_id=user_id,
            session_id=f"session_{user_id}_{agent_name}",
            debug_mode=False
        )
        
        # Run the agent
        response = user_agent.run(message, stream=stream.lower() == "true")
        
        # Format the response
        if hasattr(response, 'content'):
            content = response.content
        elif hasattr(response, 'text'):
            content = response.text
        elif isinstance(response, str):
            content = response
        elif hasattr(response, 'messages') and response.messages:
            # Handle response with messages array
            last_message = response.messages[-1]
            if hasattr(last_message, 'content'):
                content = last_message.content
            elif hasattr(last_message, 'text'):
                content = last_message.text
            else:
                content = str(last_message)
        else:
            content = str(response)
        
        logger.info(f"Agent response generated successfully (length: {len(content)})")
        
        return {
            "content": content,
            "user_id": user_id,
            "agent": agent_name,
            "timestamp": "now",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        
        # Return a helpful error response instead of raising an exception
        return {
            "content": "I apologize, but I encountered an error while processing your request. Please try again or rephrase your message.",
            "user_id": user_id,
            "agent": agent_name,
            "timestamp": "now",
            "status": "error",
            "error": str(e)
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler with helpful information."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint was not found",
            "available_endpoints": {
                "root": "/",
                "health": "/health", 
                "status": "/status",
                "agents": "/v1/agents",
                "docs": "/docs",
                "redoc": "/redoc"
            }
        }
    )

# Middleware for logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests."""
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVER_PORT", "7777"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True) 