from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

from src.agent import CryptoAgent
from src.models import CryptoNewsResponse, QueryRequest
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, LOG_LEVEL

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto Agent",
    description="A Langchain crypto Search bot, capable of using tools to access news, articles and trending topics. Using the Gemini API, and custom defined tools.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crypto_agent = CryptoAgent(
    redis_host=REDIS_HOST, 
    redis_port=REDIS_PORT,
    redis_password=REDIS_PASSWORD
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Crypto Agent is running",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.post("/query", response_model=CryptoNewsResponse)
async def process_query(request: QueryRequest):
    try:
        logger.info(f"API request received: Processing query: '{request.query}'")
        start_time = datetime.now()
        
        result = await crypto_agent.process_query(
            query=request.query,
            min_articles=request.min_articles,
            additional_context=request.additional_context
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        articles_count = len(result.get("articles", []))
        if articles_count < request.min_articles:
            logger.warning(f"Not enough articles found: {articles_count} < {request.min_articles}")
        
        logger.info(f"Query processed successfully in {processing_time:.2f} seconds: {articles_count} articles found")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)