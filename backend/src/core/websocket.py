from typing import Dict
from fastapi import WebSocket
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.last_heartbeat: Dict[str, datetime] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.last_heartbeat[client_id] = datetime.utcnow()

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.last_heartbeat:
            del self.last_heartbeat[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str, exclude: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_text(message)

    def update_heartbeat(self, client_id: str):
        if client_id in self.active_connections:
            self.last_heartbeat[client_id] = datetime.utcnow()

    def is_connected(self, client_id: str) -> bool:
        return client_id in self.active_connections

websocket_manager = WebSocketManager()
