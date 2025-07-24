import json
import modal
from loguru import logger

MAX_SESSION_TIME = 15 * 60
app = modal.App("rest-book-bot")

# Create Modal image with all dependencies and include bot.py
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_requirements("requirements.txt")
    .add_local_file("requirements.txt", "/root/requirements.txt")
    .add_local_file("bot.py", "/root/bot.py")
    .add_local_file("templates/streams.xml", "/root/templates/streams.xml")
    .add_local_file("audio_s3.py", "/root/audio_s3.py")
    .add_local_file("agent_response.py", "/root/agent_response.py")
    .add_local_file("agnoagentservice.py", "/root/agnoagentservice.py")
    .add_local_file("restraunt_data.py", "/root/restraunt_data.py")
)


# First function for handling TwiML - this is a lightweight function
@app.function(
    image=image,
    cpu=0.125,  # Lower CPU for this simple function
    memory=256,  # Less memory needed
    secrets=[modal.Secret.from_dotenv()],
    min_containers=0,
    enable_memory_snapshot=False,
)
@modal.asgi_app()
def twiml_endpoint():
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware

    web_app = FastAPI()
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @web_app.post("/twiml")
    async def start_call():
        logger.info("POST TwiML received")
        # Read the TwiML template
        with open("/root/templates/streams.xml", "r") as file:
            return HTMLResponse(
                content=file.read(),
                media_type="application/xml",
            )

    return web_app


# WebSocket endpoint function with increased resources to handle bot processing
@app.function(
    image=image,
    cpu=0.125,
    memory=300,  
    secrets=[modal.Secret.from_dotenv()],
    min_containers=1,
    buffer_containers=1,
    enable_memory_snapshot=False,
    timeout=MAX_SESSION_TIME,  # Set timeout for long-running sessions
)
@modal.asgi_app()
def websocket_endpoint():
    from fastapi import FastAPI, WebSocket
    from fastapi.middleware.cors import CORSMiddleware
    from bot import run_bot  # Import run_bot directly

    web_app = FastAPI()
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @web_app.websocket("/ws-handler")
    async def websocket_handler(websocket: WebSocket):
        try:
            await websocket.accept()
            start_data = websocket.iter_text()
            await start_data.__anext__()
            call_data = json.loads(await start_data.__anext__())
            print(call_data, flush=True)
            stream_sid = call_data["start"]["streamSid"]
            call_sid = call_data["start"]["callSid"]
            print("WebSocket connection accepted")
            await run_bot(websocket, call_sid, stream_sid)

        except Exception as e:
            logger.error(f"Error in websocket handler: {e}")
            import traceback

            logger.error(traceback.format_exc())

        logger.info("WebSocket connection closed")

    return web_app
