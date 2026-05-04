from datetime import datetime

from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    message: str
    context: dict = {}
    agent_type: str = "general"  # "general" | "quality" | "haccp" | "equipment"


class AgentChatResponse(BaseModel):
    reply: str
    confidence: float  # 0.0–1.0
    sources: list[str] = []
    suggested_actions: list[str] = []
    agent_type: str
    responded_at: datetime
