from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self) -> None:
        # room_id를 키(Key)로, 연결된 웹소켓 객체 리스트를 값(Value)으로 관리합니다.
        self.active_connections: Dict[str, List[WebSocket]] = {}


manager = ConnectionManager()

