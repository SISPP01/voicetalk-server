from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Git/Github

app = FastAPI()

class ConnectionManager:
    def __init__(self) -> None:
        # room_id를 키(Key)로, 연결된 웹소켓 객체 리스트를 값(Value)으로 관리합니다.
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str) -> None:
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        print(f"[{room_id}] 클라이언트 연결됨. 현재 인원: {len(self.active_connections[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str) -> None:
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
            print(f"[{room_id}] 클라이언트 퇴장.")

    async def broadcast_to_others(self, message: str, sender: WebSocket, room_id: str) -> None:
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != sender:
                    # 상대방에게 시그널링 데이터(JSON 문자열)를 그대로 전송합니다.
                    await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def signaling_endpoint(websocket: WebSocket, room_id: str) -> None:
    await manager.connect(websocket, room_id)
    try:
        while True:
            # 안드로이드에서 보낸 SDP(Offer/Answer) 또는 ICE Candidate 수신
            data = await websocket.receive_text()
            
            # 받은 데이터를 동일한 방에 있는 다른 Peer에게 브로드캐스트
            await manager.broadcast_to_others(data, sender=websocket, room_id=room_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
