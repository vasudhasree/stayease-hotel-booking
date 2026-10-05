from fastapi import APIRouter, WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self): self.connections=[]
    async def connect(self, ws): await ws.accept(); self.connections.append(ws)
    def disconnect(self, ws):
        if ws in self.connections: self.connections.remove(ws)
    async def broadcast(self, message):
        dead=[]
        for ws in list(self.connections):
            try: await ws.send_json(message)
            except Exception: dead.append(ws)
        for ws in dead: self.disconnect(ws)

manager=ConnectionManager()
router=APIRouter(tags=["Realtime"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect: manager.disconnect(websocket)
    except Exception: manager.disconnect(websocket)
