from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from utils.redisCache import lifespan
from routes.stockRoutes import router as stock_router
from routes.agentRoutes import router as agent_router
from routes.health import router as health_router
from starlette.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
import logging
import asyncio

templates = Jinja2Templates(directory="templates")


app = FastAPI(lifespan=lifespan, title="Agent Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(stock_router)
app.include_router(agent_router)
app.include_router(health_router)