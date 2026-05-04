import logging
import uuid
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domains.ai_agent.schemas import AgentChatRequest, AgentChatResponse

logger = logging.getLogger(__name__)


class AiAgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        if request.agent_type == "quality":
            response = await self._quality_agent(request)
        elif request.agent_type == "haccp":
            response = await self._haccp_agent(request)
        elif request.agent_type == "equipment":
            response = await self._equipment_agent(request)
        else:
            response = await self._general_agent(request)

        logger.info(f"[AI_AGENT] type={request.agent_type} confidence={response.confidence}")
        return response

    async def _general_agent(self, request: AgentChatRequest) -> AgentChatResponse:
        return AgentChatResponse(
            reply=f"안녕하세요! '{request.message}'에 대한 질문을 받았습니다. "
                  "두손푸드 AI-MES 시스템에 대해 도움을 드릴 수 있습니다. "
                  "품질분석, HACCP, 설비진단 에이전트로 전환하면 더 상세한 답변을 받으실 수 있습니다.",
            confidence=0.75,
            sources=["MES 시스템 내부 규칙"],
            suggested_actions=["품질분석 에이전트로 전환", "HACCP 에이전트로 전환"],
            agent_type=request.agent_type,
            responded_at=datetime.now(UTC),
        )

    async def _quality_agent(self, request: AgentChatRequest) -> AgentChatResponse:
        lot_id = request.context.get("lot_id")
        deviations = []

        if lot_id:
            from app.domains.quality.models import CcpRecord
            stmt = select(CcpRecord).where(
                CcpRecord.lot_id == lot_id,
                CcpRecord.is_deviation.is_(True),
            ).limit(5)
            result = await self.db.execute(stmt)
            records = result.scalars().all()
            deviations = [f"CCP {r.ccp_id}: {r.measured_value} at {r.measured_at}" for r in records]

        if deviations:
            reply = (
                f"LOT {lot_id}에 대해 {len(deviations)}건의 CCP 이탈이 감지되었습니다: "
                + "; ".join(deviations)
                + ". 즉시 시정조치가 필요합니다."
            )
            suggested = ["시정조치 기록", "LOT 보류 확인", "담당자 알림 발송"]
        else:
            reply = (
                f"'{request.message}'에 대한 품질 분석 결과: "
                "현재 감지된 CCP 이탈이 없습니다. 지속적인 모니터링을 권장합니다."
            )
            suggested = ["CCP 측정값 확인", "트렌드 분석 조회"]

        return AgentChatResponse(
            reply=reply,
            confidence=0.75,
            sources=["CCP 측정 데이터", "품질 기준 DB"],
            suggested_actions=suggested,
            agent_type=request.agent_type,
            responded_at=datetime.now(UTC),
        )

    async def _haccp_agent(self, request: AgentChatRequest) -> AgentChatResponse:
        lot_id = request.context.get("lot_id")
        failures = []

        if lot_id:
            from app.domains.haccp.models import HaccpCheckRecord
            stmt = select(HaccpCheckRecord).where(
                HaccpCheckRecord.lot_id == lot_id,
                HaccpCheckRecord.result == "FAIL",
                HaccpCheckRecord.deleted_at.is_(None),
            ).limit(5)
            result = await self.db.execute(stmt)
            records = result.scalars().all()
            failures = [f"HACCP 점검 실패: {r.checked_at} (담당: {r.checked_by})" for r in records]

        if failures:
            reply = (
                f"LOT {lot_id}에 대한 HACCP 점검 실패 {len(failures)}건이 확인되었습니다. "
                "시정조치: " + "; ".join(failures)
            )
            suggested = ["시정조치 이행 확인", "재점검 일정 수립", "관리감독자 보고"]
        else:
            reply = (
                f"'{request.message}'에 대한 HACCP 분석: "
                "현재 점검 실패 기록이 없습니다. 정기 점검 일정을 유지하세요."
            )
            suggested = ["점검 계획 확인", "다음 점검 일정 확인"]

        return AgentChatResponse(
            reply=reply,
            confidence=0.75,
            sources=["HACCP 점검 기록", "식약처 가이드라인"],
            suggested_actions=suggested,
            agent_type=request.agent_type,
            responded_at=datetime.now(UTC),
        )

    async def _equipment_agent(self, request: AgentChatRequest) -> AgentChatResponse:
        equipment_id = request.context.get("equipment_id")
        equipment_info = ""

        if equipment_id:
            from app.domains.equipment.models import Equipment
            try:
                equip_uuid = uuid.UUID(str(equipment_id))
                stmt = select(Equipment).where(Equipment.id == equip_uuid)
                result = await self.db.execute(stmt)
                equip = result.scalar_one_or_none()
                if equip:
                    equipment_info = f"설비 {equip.code} ({equip.name}) 상태: {equip.status}, OEE: {equip.oee}%"
            except (ValueError, Exception):
                pass

        reply = (
            f"'{request.message}'에 대한 설비 진단 결과. "
            + (equipment_info if equipment_info else "설비 정보를 확인 중입니다.")
            + " 정기 유지보수 일정을 준수하고 이상 징후 발생 시 즉시 보고하세요."
        )

        return AgentChatResponse(
            reply=reply,
            confidence=0.75,
            sources=["설비 상태 데이터", "유지보수 이력"],
            suggested_actions=["유지보수 일정 확인", "OEE 트렌드 분석", "설비 로그 조회"],
            agent_type=request.agent_type,
            responded_at=datetime.now(UTC),
        )

    async def get_quality_prediction(self, lot_id: uuid.UUID) -> AgentChatResponse:
        from app.domains.quality.models import CcpRecord
        stmt = select(CcpRecord).where(
            CcpRecord.lot_id == lot_id,
            CcpRecord.is_deviation.is_(True),
        ).limit(10)
        result = await self.db.execute(stmt)
        deviations = result.scalars().all()

        if deviations:
            deviation_count = len(deviations)
            confidence = max(0.6, min(0.95, 0.6 + deviation_count * 0.05))
            reply = (
                f"LOT {lot_id} 품질 예측: {deviation_count}건의 CCP 이탈이 감지되어 "
                "불합격 위험이 높습니다. 즉각적인 품질 검토가 필요합니다."
            )
            suggested = ["LOT 격리 조치", "재검사 실시", "원인 분석 착수"]
        else:
            confidence = 0.85
            reply = f"LOT {lot_id} 품질 예측: CCP 이탈 없음. 정상 품질 상태로 예측됩니다."
            suggested = ["정기 점검 유지", "출하 전 최종 검사"]

        logger.info(f"[AI_AGENT] type=quality_prediction confidence={confidence}")
        return AgentChatResponse(
            reply=reply,
            confidence=confidence,
            sources=["CCP 측정 데이터", "품질 이력 DB"],
            suggested_actions=suggested,
            agent_type="quality",
            responded_at=datetime.now(UTC),
        )
