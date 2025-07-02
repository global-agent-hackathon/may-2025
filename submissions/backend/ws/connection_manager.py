from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import asyncio


class ConnectionManager:
    """
    Manages multiple WebSocket connections and message broadcasting.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        async with self.lock:
            connections = list(self.active_connections)
        for ws in connections:
            try:
                if isinstance(message, dict):
                    await ws.send_json(message)
                else:
                    await ws.send_text(str(message))
            except WebSocketDisconnect:
                # If disconnect occurs, remove it from the list
                await self.disconnect(ws)
