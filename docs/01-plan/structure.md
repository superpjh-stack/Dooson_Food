# 두손푸드 AI-MES 폴더/파일 구조 규칙

**버전**: v1.0 | **작성일**: 2026-05-04 | **단계**: Phase 2 Convention

---

## 1. 모노레포 루트 구조

```
dooson-ai-mes/                    # 프로젝트 루트
├── apps/
│   ├── web/                      # PC 관리자 앱 (Next.js 14+)
│   ├── tablet/                   # 태블릿 현장 앱 (Next.js PWA)
│   └── mobile/                   # 모바일 점검 앱 (Next.js PWA)
├── services/
│   ├── api/                      # FastAPI 백엔드 (Modular Monolith)
│   └── ml/                       # ML 추론 서비스 (Ray Serve)
├── packages/
│   ├── types/                    # 공유 TypeScript 타입
│   └── ui/                       # 공유 UI 컴포넌트
├── infra/
│   ├── docker/                   # Docker Compose 파일
│   ├── k3s/                      # K3s 배포 매니페스트
│   └── scripts/                  # 배포/마이그레이션 스크립트
├── docs/
│   ├── 01-plan/                  # 기획 문서 (glossary, schema, naming)
│   ├── 02-design/                # 설계 문서 (UI, ARCH)
│   ├── 03-analysis/              # Gap 분석 보고서
│   └── 04-report/                # PDCA 완료 보고서
├── CLAUDE.md
├── CONVENTIONS.md
└── .env.example
```

---

## 2. Frontend (Next.js) 구조

### 2.1 공통 구조 (apps/web, apps/tablet, apps/mobile)

```
apps/web/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/
│   │   │   └── login/page.tsx
│   │   ├── (dashboard)/          # Route Group (레이아웃 공유)
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx          # 메인 KPI 대시보드
│   │   │   ├── production/
│   │   │   │   ├── page.tsx      # 생산 현황
│   │   │   │   └── [id]/page.tsx # 작업지시 상세
│   │   │   ├── lot/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── trace/page.tsx
│   │   │   ├── quality/
│   │   │   ├── equipment/
│   │   │   └── haccp/
│   │   └── api/                  # Next.js API Routes (BFF layer)
│   │       └── [...]/route.ts
│   │
│   ├── components/               # 재사용 UI 컴포넌트
│   │   ├── ui/                   # shadcn/ui 기반 기본 컴포넌트
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   └── badge.tsx
│   │   ├── charts/               # 도메인 차트 컴포넌트
│   │   │   ├── FValueChart.tsx
│   │   │   ├── OeeGauge.tsx
│   │   │   └── SensorTimeline.tsx
│   │   ├── lot/                  # LOT 관련 컴포넌트
│   │   │   ├── LotTree.tsx
│   │   │   ├── LotStatusBadge.tsx
│   │   │   └── LotTracePanel.tsx
│   │   ├── production/
│   │   ├── quality/
│   │   ├── equipment/
│   │   ├── haccp/
│   │   ├── ai/                   # AI Agent UI
│   │   │   └── AgentChatPanel.tsx
│   │   ├── alerts/
│   │   │   └── AlertCenter.tsx
│   │   └── layout/               # 레이아웃 컴포넌트
│   │       ├── Sidebar.tsx
│   │       └── TopBar.tsx
│   │
│   ├── hooks/                    # 커스텀 React Hooks
│   │   ├── use-lot-trace.ts
│   │   ├── use-work-order.ts
│   │   ├── use-ccp-monitor.ts
│   │   ├── use-sensor-stream.ts  # WebSocket 훅
│   │   └── use-notifications.ts
│   │
│   ├── services/                 # API 호출 함수 (도메인별)
│   │   ├── production.service.ts
│   │   ├── lot.service.ts
│   │   ├── quality.service.ts
│   │   ├── equipment.service.ts
│   │   └── haccp.service.ts
│   │
│   ├── stores/                   # Zustand 상태 스토어
│   │   ├── alert.store.ts
│   │   └── user.store.ts
│   │
│   ├── types/                    # TypeScript 타입 정의
│   │   ├── lot.types.ts
│   │   ├── work-order.types.ts
│   │   ├── quality.types.ts
│   │   └── api.types.ts
│   │
│   └── lib/                      # 인프라/유틸
│       ├── api/
│       │   └── client.ts         # Axios 인스턴스 + 인터셉터
│       ├── socket/
│       │   └── client.ts         # Socket.io 연결
│       ├── utils/
│       │   ├── lot-code.ts       # LOT 코드 생성/파싱
│       │   ├── format-date.ts
│       │   └── oee-calculator.ts
│       └── env.ts                # 환경변수 검증 (zod)
│
├── public/
├── .env.local                    # Git 제외
├── .env.example
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### 2.2 컴포넌트 파일 내부 구조

```typescript
// 컴포넌트 파일 구조 순서
// 1. imports (외부 → 내부 순)
// 2. types/interfaces
// 3. constants (컴포넌트 전용)
// 4. subcomponents (필요시)
// 5. main component (default export)
// 6. 보조 export

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { lotService } from '@/services/lot.service'
import type { Lot } from '@/types/lot.types'

interface LotStatusBadgeProps {
  status: Lot['status']
  size?: 'sm' | 'md'
}

const STATUS_LABEL: Record<Lot['status'], string> = {
  ACTIVE: '활성',
  ON_HOLD: '보류',
  CONSUMED: '소비됨',
  SHIPPED: '출하',
  RECALLED: '회수',
}

export function LotStatusBadge({ status, size = 'md' }: LotStatusBadgeProps) {
  // ...
}
```

---

## 3. Backend (FastAPI) 구조

```
services/api/
├── app/
│   ├── main.py                   # FastAPI 앱 엔트리포인트
│   ├── config.py                 # 설정 (Pydantic Settings)
│   ├── dependencies.py           # 공통 DI (DB 세션, 현재 사용자)
│   │
│   ├── domains/                  # 도메인별 모듈
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py        # Pydantic 모델
│   │   │   └── models.py         # SQLAlchemy 모델
│   │   ├── production/
│   │   │   ├── router.py         # /api/v1/production/...
│   │   │   ├── service.py
│   │   │   ├── repository.py     # DB 쿼리 캡슐화
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── lot/                  # LOT + LotLineage
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── trace_service.py  # 역추적/전방추적 전용
│   │   │   ├── repository.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── quality/              # CCP, F-value, X-Ray
│   │   ├── equipment/            # 설비, 정비, OEE
│   │   ├── haccp/
│   │   ├── ai_agent/             # LangGraph AI Agent Hub
│   │   │   ├── router.py
│   │   │   ├── agents/
│   │   │   │   ├── production_agent.py
│   │   │   │   ├── quality_agent.py
│   │   │   │   ├── haccp_agent.py
│   │   │   │   └── equipment_agent.py
│   │   │   └── rag/
│   │   │       └── haccp_rag.py
│   │   └── notification/
│   │
│   ├── infrastructure/
│   │   ├── database.py           # SQLAlchemy 엔진 + 세션
│   │   ├── redis.py              # Redis 클라이언트
│   │   ├── mqtt.py               # MQTT 구독/발행
│   │   ├── storage.py            # MinIO 클라이언트
│   │   └── websocket.py          # Socket.io 서버
│   │
│   └── shared/
│       ├── exceptions.py         # 공통 예외 클래스
│       ├── pagination.py         # 페이지네이션 스키마
│       └── base_model.py         # SQLAlchemy Base + 공통 컬럼
│
├── alembic/
│   ├── versions/                 # 마이그레이션 파일
│   └── env.py
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── .env.example
```

### 3.1 도메인 모듈 내부 파일 역할

| 파일 | 역할 | 계층 |
|------|------|------|
| `router.py` | HTTP 엔드포인트 정의, 의존성 주입 | Presentation |
| `service.py` | 비즈니스 로직 (트랜잭션 경계) | Application |
| `repository.py` | DB 쿼리 캡슐화 | Infrastructure |
| `schemas.py` | Pydantic 요청/응답 모델 | Domain |
| `models.py` | SQLAlchemy ORM 모델 | Infrastructure |

### 3.2 Router → Service → Repository 흐름

```python
# router.py — HTTP 처리만
@router.post("/work-orders", response_model=WorkOrderResponse)
async def create_work_order(
    payload: WorkOrderCreate,
    service: WorkOrderService = Depends(get_work_order_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create(payload, created_by=current_user.id)

# service.py — 비즈니스 로직
class WorkOrderService:
    async def create(self, payload: WorkOrderCreate, created_by: UUID) -> WorkOrder:
        bom = await self.bom_repo.get_active(payload.product_id)
        wo = await self.repo.create(payload, bom_id=bom.id, created_by=created_by)
        await self.notification_service.notify_workers(wo)
        return wo

# repository.py — DB 쿼리만
class WorkOrderRepository:
    async def create(self, payload, bom_id, created_by) -> WorkOrder:
        wo = WorkOrderModel(**payload.model_dump(), bom_id=bom_id, created_by=created_by)
        self.db.add(wo)
        await self.db.flush()
        return wo
```

---

## 4. 파일 분리 기준

### 4.1 컴포넌트 분리 기준
- JSX 50줄 초과 → 분리
- 동일 패턴 2회 이상 → 추출
- 독립 상태 존재 → 분리
- 다른 페이지에서도 사용 → `components/` 이동

### 4.2 서비스 분리 기준
- 비즈니스 로직 100줄 초과 → 서브 서비스 분리
  - `lot_trace_service.py` (역추적 전용)
  - `f_value_service.py` (F-value 계산 전용)
- 외부 시스템 연동 → `infrastructure/`로 분리

### 4.3 신규 파일 위치 결정 흐름
```
이 코드가 특정 도메인에만 관련되나?
  → YES: 해당 도메인 폴더 내부
  → NO: 두 개 이상 도메인에서 사용?
         → YES: shared/ 또는 packages/types/
         → NO: 프로젝트 전반? → lib/ 또는 utils/
```

---

## 5. 테스트 파일 구조

```
tests/
├── unit/
│   ├── test_lot_trace_service.py    # Service 단위 테스트
│   ├── test_f_value_calculator.py
│   └── test_oee_calculator.py
├── integration/
│   ├── test_work_order_api.py       # API 통합 테스트 (실 DB)
│   └── test_lot_lineage_query.py    # Closure Table 쿼리 성능 테스트
└── conftest.py                      # pytest fixtures
```

- 테스트 파일명: `test_{테스트_대상}.py`
- DB 목(Mock) 사용 금지 — 실제 테스트 DB 사용 (docker compose)
- LOT 역추적 쿼리는 반드시 **5초 이내** 성능 테스트 포함
