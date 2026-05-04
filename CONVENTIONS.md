# 두손푸드 AI-MES 코딩 컨벤션

**버전**: v1.0 | **작성일**: 2026-05-04
**상세 규칙**: `docs/01-plan/naming.md`, `docs/01-plan/structure.md`

---

## 1. 네이밍 요약

| 대상 | 규칙 | 예시 |
|------|------|------|
| React 컴포넌트 | PascalCase | `LotTree`, `FValueChart` |
| TS 함수/변수 | camelCase | `fetchLotLineage`, `workOrderId` |
| TS 상수 | UPPER_SNAKE_CASE | `LOT_STATUS`, `CCP_LIMIT_TEMP` |
| Python 함수/변수 | snake_case | `get_lot_lineage`, `work_order_id` |
| Python 클래스 | PascalCase | `WorkOrderService`, `LotRepository` |
| DB 컬럼 | snake_case | `work_order_id`, `f0_calculated` |
| API 엔드포인트 | kebab-case 복수형 | `/work-orders`, `/lot-lineage` |
| 환경변수 | UPPER_SNAKE_CASE + 접두사 | `DB_HOST`, `NEXT_PUBLIC_API_URL` |

---

## 2. 코드 스타일

### TypeScript / JavaScript
```jsonc
// .eslintrc 설정 요약
{
  "extends": ["next/core-web-vitals", "typescript-eslint/recommended"],
  "rules": {
    "quotes": ["error", "single"],       // 홑따옴표
    "semi": ["error", "never"],          // 세미콜론 없음
    "indent": ["error", 2],              // 2칸 들여쓰기
    "@typescript-eslint/no-explicit-any": "error",  // any 금지
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

### Python
```toml
# pyproject.toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N"]

[tool.black]
line-length = 100
```

---

## 3. TypeScript 패턴

### API 호출 (서비스 → 훅 → 컴포넌트)
```typescript
// services/lot.service.ts
export const lotService = {
  getLineage: (lotId: string) =>
    apiClient.get<LotLineageResponse>(`/lots/${lotId}/trace/backward`),
}

// hooks/use-lot-trace.ts
export function useLotTrace(lotId: string) {
  return useQuery({
    queryKey: ['lot', lotId, 'trace'],
    queryFn: () => lotService.getLineage(lotId),
  })
}

// 컴포넌트에서 직접 apiClient 호출 금지
```

### 상태 타입 상수 (MES 도메인)
```typescript
export const LOT_STATUS = {
  ACTIVE: 'ACTIVE',
  ON_HOLD: 'ON_HOLD',
  CONSUMED: 'CONSUMED',
  SHIPPED: 'SHIPPED',
  RECALLED: 'RECALLED',
} as const
export type LotStatus = typeof LOT_STATUS[keyof typeof LOT_STATUS]

export const WORK_ORDER_STATUS = {
  PLANNED: 'PLANNED',
  RELEASED: 'RELEASED',
  IN_PROGRESS: 'IN_PROGRESS',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED',
} as const

export const SEVERITY = {
  CRITICAL: 'CRITICAL',
  WARNING: 'WARNING',
  INFO: 'INFO',
} as const
```

### AI 결과 표시 (필수 규칙)
```typescript
// AI 예측 결과를 표시할 때는 반드시 confidence + source 함께 표시
interface AiPrediction {
  value: number | string
  confidence: number       // 0~1
  modelName: string        // 'LSTM-v2', 'XGBoost-CCP-v1'
  predictedAt: string
  source?: string          // RAG일 경우 출처 문서명
}

// 신뢰도 < 0.6: 표시하지 않음 (UI 규칙)
// 신뢰도 0.6~0.8: 주의 표시
// 신뢰도 >= 0.8: 고신뢰 표시
```

---

## 4. Python 패턴

### Pydantic 스키마 구조
```python
# 기본 패턴: Create / Update / Response 분리
class WorkOrderBase(BaseModel):
    product_id: UUID
    qty_target: Decimal
    scheduled_date: date

class WorkOrderCreate(WorkOrderBase):
    line_id: UUID | None = None

class WorkOrderUpdate(BaseModel):
    status: WorkOrderStatus | None = None
    line_id: UUID | None = None

class WorkOrderResponse(WorkOrderBase):
    id: UUID
    code: str
    status: WorkOrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### 비동기 DB 접근
```python
# async/await 필수 — 동기 쿼리 사용 금지
async def get_lot_lineage(self, lot_id: UUID, direction: str) -> list[Lot]:
    if direction == "backward":
        stmt = (
            select(Lot)
            .join(LotLineage, LotLineage.ancestor_lot_id == Lot.id)
            .where(LotLineage.descendant_lot_id == lot_id)
            .order_by(LotLineage.depth)
        )
    result = await self.db.execute(stmt)
    return result.scalars().all()
```

### 예외 처리
```python
# 도메인 예외는 shared/exceptions.py에서 정의
class LotNotFoundException(MesBaseException):
    status_code = 404
    detail = "LOT를 찾을 수 없습니다"

class CcpDeviationException(MesBaseException):
    status_code = 422
    detail = "CCP 기준값 이탈 감지됨"

# Router에서 try/except 사용 금지 — 글로벌 핸들러 사용
```

---

## 5. 환경변수 (.env.example)

```bash
# ===== App =====
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# ===== Database =====
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dooson_mes
DB_USER=mes_user
DB_PASSWORD=

# ===== Redis =====
REDIS_URL=redis://localhost:6379

# ===== Auth (JWT) =====
AUTH_SECRET=                    # openssl rand -base64 32
AUTH_ACCESS_TOKEN_EXPIRE=3600   # 초 단위 (1시간)
AUTH_REFRESH_TOKEN_EXPIRE=604800

# ===== Storage (MinIO/S3) =====
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_ACCESS_KEY=
STORAGE_SECRET_KEY=
STORAGE_BUCKET_XRAY=dooson-xray
STORAGE_BUCKET_REPORTS=dooson-reports

# ===== IoT / MQTT =====
IOT_MQTT_HOST=localhost
IOT_MQTT_PORT=1883
IOT_MQTT_USERNAME=
IOT_MQTT_PASSWORD=

# ===== AI/ML =====
LLM_PROVIDER=anthropic           # anthropic | openai
LLM_API_KEY=
LLM_MODEL=claude-sonnet-4-6
ML_MODEL_PATH=/models
ML_INFERENCE_URL=http://localhost:8001

# ===== Monitoring =====
SENTRY_DSN=
```

---

## 6. Clean Architecture 의존성 방향

```
Presentation (components, pages, hooks)
    ↓ 호출 가능
Application (services, use-cases)
    ↓ 호출 가능
Infrastructure (api/client, socket, db)
    ↑ 의존 가능
Domain (types, constants, entities)

규칙: 상위 레이어는 하위 레이어에만 의존
      Domain은 어디에도 의존하지 않음
      컴포넌트에서 apiClient 직접 호출 금지
```

---

## 7. MES 도메인 필수 규칙

1. **LOT 상태 자동 변경**: CCP 이탈, X-Ray NG 발생 시 코드에서 직접 `ON_HOLD` 변경 금지 → `LotService.hold()` 메서드를 통해서만 처리 (이벤트 + 알림 동시 발행)
2. **AI 결과 표시**: confidence 없는 AI 예측값 UI 노출 금지
3. **HACCP 기록 삭제 금지**: `deleted_at` soft delete 사용, 하드 삭제 불가
4. **BOM 버전 고정**: `WorkOrder` 생성 시점의 BOM ID를 고정 저장 — 이후 BOM 변경 영향 없음
5. **TimescaleDB Hypertable**: 시계열 테이블에 일반 `INSERT` 사용 가능, `UPDATE/DELETE`는 성능 이슈로 지양
6. **Closure Table 갱신**: LOT 생성 시 반드시 `lot_lineage` 행을 트랜잭션 내에서 동시 삽입

---

## 8. Git 컨벤션

### 커밋 메시지
```
{type}({scope}): {설명}

type: feat | fix | refactor | docs | test | chore | perf
scope: production | lot | quality | equipment | haccp | ai | infra

예시:
feat(lot): LOT Closure Table 역추적 쿼리 구현
fix(quality): CCP 이탈 감지 임계값 비교 오류 수정
perf(lot): lot_lineage 인덱스 추가로 역추적 성능 개선
docs(schema): F-value 시계열 테이블 Hypertable 설명 추가
```

### 브랜치 전략
```
main          # 프로덕션
develop       # 통합 개발
feature/{도메인}-{기능}   # feature/lot-closure-table
fix/{도메인}-{이슈}       # fix/quality-ccp-threshold
```
