import uuid
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.ai_agent.schemas import AgentChatRequest, AgentChatResponse
from app.domains.ai_agent.service import AiAgentService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai-agent"])


def get_ai_agent_service(db: AsyncSession = Depends(get_db)) -> AiAgentService:
    return AiAgentService(db)


@router.post("/chat", response_model=AgentChatResponse)
async def chat(
    request: AgentChatRequest,
    service: AiAgentService = Depends(get_ai_agent_service),
):
    logger.info(f"[API] POST /ai/chat agent_type={request.agent_type}")
    return await service.chat(request)


@router.get("/quality-prediction/{lot_id}", response_model=AgentChatResponse)
async def get_quality_prediction(
    lot_id: uuid.UUID,
    service: AiAgentService = Depends(get_ai_agent_service),
):
    logger.info(f"[API] GET /ai/quality-prediction/{lot_id}")
    return await service.get_quality_prediction(lot_id)


@router.get("/health")
async def ai_health():
    return {"status": "ok", "model": "rule-based"}
