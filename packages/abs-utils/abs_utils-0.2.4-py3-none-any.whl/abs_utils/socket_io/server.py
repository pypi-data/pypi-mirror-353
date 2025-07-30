import socketio
from fastapi import FastAPI
from typing import Callable, Dict, Any
from functools import wraps
import asyncio


class SocketIOService:
    def __init__(self, cors_origins: str = "*"):
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=cors_origins)

    def bind_app(self, fastapi_app: FastAPI):
        return socketio.ASGIApp(self.sio, other_asgi_app=fastapi_app)

    async def emit_to_sid(self, sid: str, event: str, data: Dict[str, Any]):
        """Emit directly to a specific client."""
        await self.sio.emit(event, data, to=sid)

    async def emit_broadcast(self, event: str, data: Dict[str, Any]):
        """Emit to all clients."""
        await self.sio.emit(event, data)
