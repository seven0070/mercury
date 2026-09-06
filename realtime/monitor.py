import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from components.surfsense import SurfSense
from components.ghost_pepper import GhostPepper

app = FastAPI(title="Mercury Real-Time Monitor")
clients = []
surf = SurfSense()
pepper = GhostPepper()

async def broadcast(message: str):
    disconnected = []
    for client in clients:
        try:
            await client.send_text(message)
        except Exception:
            disconnected.append(client)
    for client in disconnected:
        if client in clients:
            clients.remove(client)

async def monitor_loop():
    while True:
        try:
            raw_json = surf.gather("latest")
            processed = pepper.process(raw_json)
            data = json.loads(processed)
            update = {
                "type": "update",
                "headlines": data.get("headlines", []),
                "top_terms": data.get("top_terms", [])
            }
            await broadcast(json.dumps(update))
        except Exception as e:
            print(f"Monitor error: {e}")
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_loop())

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)
