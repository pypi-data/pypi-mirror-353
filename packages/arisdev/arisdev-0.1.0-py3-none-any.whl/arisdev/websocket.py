"""
WebSocket handler untuk ArisDev Framework
"""

import asyncio
import websockets
import json
from typing import Dict, Set, Callable, Any

class WebSocket:
    """WebSocket handler untuk ArisDev Framework"""
    
    def __init__(self, app):
        """Inisialisasi WebSocket
        
        Args:
            app: Framework instance
        """
        self.app = app
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.rooms: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.handlers: Dict[str, Callable] = {}
        self.server = None
    
    async def handle(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle WebSocket connection
        
        Args:
            websocket: WebSocket connection
            path (str): WebSocket path
        """
        self.clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    event = data.get("event")
                    if event in self.handlers:
                        await self.handlers[event](websocket, data.get("data"))
                except json.JSONDecodeError:
                    pass
        finally:
            self.clients.remove(websocket)
            for room in self.rooms.values():
                room.discard(websocket)
    
    def on(self, event: str):
        """Decorator untuk menambahkan event handler
        
        Args:
            event (str): Event name
        """
        def decorator(func: Callable):
            self.handlers[event] = func
            return func
        return decorator
    
    async def broadcast(self, event: str, data: Any, room: str = None):
        """Broadcast message ke semua client atau room
        
        Args:
            event (str): Event name
            data: Event data
            room (str): Room name
        """
        message = json.dumps({
            "event": event,
            "data": data
        })
        
        if room and room in self.rooms:
            websockets = self.rooms[room]
        else:
            websockets = self.clients
        
        if websockets:
            await asyncio.gather(
                *[ws.send(message) for ws in websockets]
            )
    
    async def send(self, websocket: websockets.WebSocketServerProtocol, event: str, data: Any):
        """Send message ke client
        
        Args:
            websocket: WebSocket connection
            event (str): Event name
            data: Event data
        """
        message = json.dumps({
            "event": event,
            "data": data
        })
        await websocket.send(message)
    
    def join_room(self, websocket: websockets.WebSocketServerProtocol, room: str):
        """Join room
        
        Args:
            websocket: WebSocket connection
            room (str): Room name
        """
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(websocket)
    
    def leave_room(self, websocket: websockets.WebSocketServerProtocol, room: str):
        """Leave room
        
        Args:
            websocket: WebSocket connection
            room (str): Room name
        """
        if room in self.rooms:
            self.rooms[room].discard(websocket)
            if not self.rooms[room]:
                del self.rooms[room]
    
    def get_room_clients(self, room: str) -> Set[websockets.WebSocketServerProtocol]:
        """Get clients in room
        
        Args:
            room (str): Room name
        """
        return self.rooms.get(room, set())
    
    def get_client_count(self) -> int:
        """Get total client count"""
        return len(self.clients)
    
    def get_room_count(self) -> int:
        """Get total room count"""
        return len(self.rooms)
    
    async def start(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server
        
        Args:
            host (str): Server host
            port (int): Server port
        """
        self.server = await websockets.serve(self.handle, host, port)
        await self.server.wait_closed()
    
    def stop(self):
        """Stop WebSocket server"""
        if self.server:
            self.server.close() 