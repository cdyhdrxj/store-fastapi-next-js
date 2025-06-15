from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)
    
    async def notify_managers_about_buying(self, username: str, item: str, quantity: int):
        message = {
            "username": username,
            "item": item,
            "quantity": quantity, 
        }
        await self.broadcast(json.dumps(message))
