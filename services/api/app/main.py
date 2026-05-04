import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.domains.ai_agent.router import router as ai_router
from app.domains.auth.router import router as auth_router
from app.domains.equipment.router import router as equipment_router
from app.domains.haccp.router import router as haccp_router
from app.domains.lot.router import router as lot_router
from app.domains.notification.router import router as notification_router
from app.domains.product.router import router as product_router
from app.domains.production.router import router as production_router
from app.domains.quality.router import router as quality_router
from app.shared.exceptions import MesException, mes_exception_handler

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

connected_ws: list[WebSocket] = []


async def broadcast_notification(notification_data: dict) -> None:
    dead = []
    for ws in connected_ws:
        try:
            await ws.send_json(notification_data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in connected_ws:
            connected_ws.remove(ws)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"[STARTUP] {settings.app_name} 시작")
    logger.info(f"[STARTUP] DB: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    yield
    logger.info("[SHUTDOWN] 서버 종료")


app = FastAPI(
    title="두손푸드 AI-MES API",
    version="0.1.0",
    description="제조AI특화 스마트공장 MES 백엔드",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(MesException, mes_exception_handler)

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(lot_router, prefix="/api/v1")
app.include_router(quality_router, prefix="/api/v1")
app.include_router(production_router, prefix="/api/v1")
app.include_router(equipment_router, prefix="/api/v1")
app.include_router(haccp_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(notification_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")


@app.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket):
    await websocket.accept()
    connected_ws.append(websocket)
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        if websocket in connected_ws:
            connected_ws.remove(websocket)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
