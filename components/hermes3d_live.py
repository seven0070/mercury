import os
import json
import asyncio
import websockets
import threading
import time

class Hermes3DLiveClient:
    """
    Sends live status updates to Hermes3D 3D office via WebSocket.
    Uses environment variables:
        HERMES3D_LIVE_ENABLED (default 'false')
        HERMES3D_GATEWAY_URL (default 'ws://localhost:18789')
        HERMES3D_GATEWAY_TOKEN (optional)
    """
    def __init__(self):
        self.enabled = os.getenv("HERMES3D_LIVE_ENABLED", "false").lower() == "true"
        self.gateway_url = os.getenv("HERMES3D_GATEWAY_URL", "ws://localhost:18789")
        self.token = os.getenv("HERMES3D_GATEWAY_TOKEN", "")
        self.connection = None
        self.loop = None
        self.thread = None

    def connect(self):
        """Establish WebSocket connection in a background thread."""
        if not self.enabled:
            return

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._maintain_connection())

    async def _maintain_connection(self):
        while True:
            if not self.connection:
                await self._connect_async()
            await asyncio.sleep(5)

    async def _connect_async(self):
        try:
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            self.connection = await websockets.connect(self.gateway_url, extra_headers=headers)
            print(f"Connected to Hermes3D gateway at {self.gateway_url}")
        except Exception as e:
            print(f"Failed to connect to Hermes3D gateway: {e}")
            self.connection = None

    def send_status(self, agent_name: str, status: str, message: str):
        """
        Send a status update to Hermes3D.
        agent_name: e.g., 'data_collector', 'processor', 'visualizer'
        status: 'working', 'idle', 'completed', 'error'
        message: Human-readable description
        """
        if not self.enabled or not self.connection:
            return

        payload = {
            "type": "agent_status",
            "agent_id": agent_name,
            "status": status,
            "message": message,
            "timestamp": time.time()
        }

        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._send_async(json.dumps(payload)),
                self.loop
            )
        else:
            print("Hermes3D live loop not running, status not sent.")

    async def _send_async(self, data: str):
        try:
            await self.connection.send(data)
        except Exception as e:
            print(f"Error sending to Hermes3D: {e}")
            self.connection = None
            await self._connect_async()

    def close(self):
        if self.loop and self.connection:
            asyncio.run_coroutine_threadsafe(self.connection.close(), self.loop)
