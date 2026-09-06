import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
from pi_client import PiClient

load_dotenv()

app = FastAPI(title="Mercury Pi Middleware", version="0.4")
pi = PiClient()
MERCURY_EXECUTE_URL = os.getenv("MERCURY_EXECUTE_URL", "http://localhost:8000/execute")
MERCURY_API_KEY = os.getenv("MERCURY_API_KEY", "")
PI_API_KEY = os.getenv("PI_API_KEY", "")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

def verify_api_key(x_api_key: str = Header(None)):
    if PI_API_KEY and x_api_key != PI_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    goal = pi.extract_goal(request.message)
    if not goal:
        raise HTTPException(status_code=400, detail="Could not understand the request.")

    headers = {}
    if MERCURY_API_KEY:
        headers["X-API-Key"] = MERCURY_API_KEY

    try:
        resp = requests.post(
            MERCURY_EXECUTE_URL,
            json={"goal": goal},
            headers=headers,
            timeout=60
        )
        resp.raise_for_status()
        pipeline_result = resp.json()["result"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    reply = pi.generate_response(pipeline_result, request.message)
    return ChatResponse(reply=reply)

@app.get("/health")
async def health():
    return {"status": "ok"}
