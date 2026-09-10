import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings, STORAGE_DIR
from app.core.logging import logger
from app.database.database import init_db, SessionLocal
from app.database.repositories.sop_repo import SopRepository
from app.sop.rule_loader import RuleLoader
from app.intelligence.zones import DEFAULT_ZONES

from app.api.routes.videos import router as videos_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.assistant import router as assistant_router
from app.api.routes.sop import router as sop_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.system import router as system_router
from app.api.websocket import manager as ws_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CargoIQ backend service...")
    init_db()
    # Seed SOP rules and zones in DB
    db = SessionLocal()
    try:
        sop_repo = SopRepository(db)
        rules = RuleLoader.load_rules()
        for code, r in rules.items():
            sop_repo.upsert(
                code=code,
                name=r.get("name", code),
                severity=r.get("severity", "HIGH"),
                conditions=r.get("conditions", {}),
                recommendation=r.get("recommendation", ""),
                description=r.get("description", "")
            )
        for z in DEFAULT_ZONES:
            sop_repo.upsert_zone(
                name=z["name"],
                polygon=z["polygon"],
                description=z.get("description", ""),
                color=z.get("color", "#3b82f6")
            )
    finally:
        db.close()
    logger.info("Database and SOP rules initialized.")
    yield
    logger.info("Shutting down CargoIQ backend service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.TAGLINE,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage directory for static video, clip, and thumbnail playback
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

# Include API Routers
app.include_router(videos_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(assistant_router, prefix="/api")
app.include_router(sop_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(system_router, prefix="/api")

# WebSocket Endpoint
@app.websocket("/ws/analysis/{job_id}")
async def websocket_analysis_endpoint(websocket: WebSocket, job_id: str):
    await ws_manager.connect(websocket, job_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Client heartbeat ping
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)

@app.get("/")
def root_info():
    return {
        "name": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
