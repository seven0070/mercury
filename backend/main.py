import os
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import structlog
from prometheus_fastapi_instrumentator import Instrumentator

# Load environment variables from .env file
load_dotenv()

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()

# Add project root to path so we can import crew.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crew import run_crew
from database import init_db, SessionLocal, QueryRecord

app = FastAPI(title="Mercury API", version="1.0")

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# CORS configuration
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

MERCURY_API_KEY = os.getenv("MERCURY_API_KEY", "")

class ExecuteRequest(BaseModel):
    goal: str
    connector: str = "google_search"

class ExecuteResponse(BaseModel):
    result: str
    history_id: int = None

def verify_api_key(x_api_key: str = Header(None)):
    if MERCURY_API_KEY and x_api_key != MERCURY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.on_event("startup")
def on_startup():
    logger.info("Initializing database")
    init_db()
    logger.info("Database initialized")

@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest, api_key: str = Header(None, alias="X-API-Key")):
    verify_api_key(api_key)
    logger.info("Executing request", goal=request.goal, connector=request.connector)
    try:
        output = run_crew(request.goal, request.connector)

        # Save record to database
        db: Session = SessionLocal()
        record = QueryRecord(goal=request.goal, connector=request.connector, result=output, created_at=datetime.utcnow())
        db.add(record)
        db.commit()
        db.refresh(record)
        db.close()
        
        logger.info("Request completed", history_id=record.id)

        return ExecuteResponse(result=output, history_id=record.id)
    except Exception as e:
        logger.error("Request failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    db: Session = SessionLocal()
    records = db.query(QueryRecord).order_by(QueryRecord.created_at.desc()).limit(20).all()
    db.close()
    return [
        {
            "id": r.id,
            "goal": r.goal,
            "connector": r.connector,
            "created_at": r.created_at.isoformat(),
            "result_preview": r.result[:200] + "..." if len(r.result) > 200 else r.result
        }
        for r in records
    ]

@app.get("/health")
async def health():
    return {"status": "ok"}
