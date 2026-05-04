# 두손푸드 AI-MES 네이밍 규칙

**버전**: v1.0 | **작성일**: 2026-05-04 | **단계**: Phase 2 Convention

---

## 1. 공통 원칙

- **영어** 사용 (주석, 문서는 한국어 허용)
- 약어 지양 — `wo`(X) → `workOrder`(O), `eq`(X) → `equipment`(O)
- MES 도메인 용어는 `glossary.md`의 영어 코드명을 따름

---

## 2. 언어별 네이밍 규칙

### 2.1 TypeScript / JavaScript (프론트엔드)

| 대상 | 규칙 | 예시 |
|------|------|------|
| 파일명 (컴포넌트) | PascalCase | `LotTree.tsx`, `FValueChart.tsx` |
| 파일명 (유틸/훅) | kebab-case | `use-lot-trace.ts`, `format-date.ts` |
| 파일명 (상수) | kebab-case | `lot-status.const.ts` |
| React 컴포넌트 | PascalCase | `WorkOrderTable`, `CcpAlertBadge` |
| 함수 | camelCase | `fetchLotLineage`, `calculateOEE` |
| 변수 | camelCase | `workOrderId`, `fValueRecord` |
| 상수 | UPPER_SNAKE_CASE | `LOT_STATUS`, `CCP_LIMIT_TEMP` |
| 타입/인터페이스 | PascalCase | `WorkOrder`, `LotLineageNode` |
| Enum | PascalCase (키는 UPPER) | `LotStatus.ON_HOLD` |
| CSS 클래스 | kebab-case (Tailwind 사용) | `lot-tree-node`, `fvalue-chart` |
| React Hook | `use` 접두사 + camelCase | `useLotTrace`, `useWorkOrderList` |

### 2.2 Python (FastAPI 백엔드)

| 대상 | 규칙 | 예시 |
|------|------|------|
| 파일명 | snake_case | `lot_router.py`, `work_order_service.py` |
| 함수 | snake_case | `get_lot_lineage`, `create_work_order` |
| 변수 | snake_case | `work_order_id`, `f_value_record` |
| 클래스 | PascalCase | `WorkOrderService`, `LotRepository` |
| 상수 | UPPER_SNAKE_CASE | `CCP_DEVIATION_THRESHOLD`, `LOT_CODE_PREFIX` |
| Pydantic 모델 | PascalCase | `WorkOrderCreate`, `LotResponse` |
| SQLAlchemy 모델 | PascalCase | `WorkOrder`, `LotLineage` |
| DB 테이블명 | snake_case (복수형) | `work_orders`, `lot_lineages` |
| DB 컬럼명 | snake_case | `work_order_id`, `f0_calculated` |

### 2.3 파일/폴더 구조

| 대상 | 규칙 | 예시 |
|------|------|------|
| 도메인 폴더 | snake_case | `lot_traceability/`, `f_value/` |
| Next.js 라우트 | kebab-case | `work-orders/`, `lot-trace/` |
| 환경변수 | UPPER_SNAKE_CASE + 접두사 | `DB_HOST`, `NEXT_PUBLIC_API_URL` |

---

## 3. MES 도메인 코드 네이밍

### 3.1 LOT 코드 형식
```
DS-{YYYYMMDD}-{제품코드}-{4자리순번}
예: DS-20261201-HMR001-0001

- DS: 두손(DooSon) 공장 코드
- 날짜: 생산/입고일
- 제품코드: products.code
- 순번: 당일 4자리 시퀀스
```

### 3.2 작업지시 코드 형식
```
WO-{YYYYMMDD}-{4자리순번}
예: WO-20261201-0001
```

### 3.3 API 엔드포인트 (REST)
```
/api/v1/{도메인}/{리소스}[/{id}][/{액션}]

GET    /api/v1/production/work-orders
POST   /api/v1/production/work-orders
GET    /api/v1/lots/{lot_id}/trace/backward
GET    /api/v1/lots/{lot_id}/trace/forward
POST   /api/v1/quality/ccp-records
GET    /api/v1/equipment/{equipment_id}/sensors  (WebSocket)
```
- 복수형 명사 사용
- kebab-case
- 동사형 액션은 마지막에: `/trace/backward`, `/hold`, `/release`

### 3.4 WebSocket 이벤트명
```
snake_case 사용
서버→클라이언트: {도메인}:{이벤트}
  sensor:reading_updated
  ccp:deviation_detected
  lot:status_changed
  equipment:fault_predicted
  notification:created
```

### 3.5 Celery 태스크명
```
{도메인}.{액션}
  production.generate_work_order_report
  quality.calculate_f_value
  ai.run_anomaly_detection
  kpi.aggregate_hourly_oee
```

### 3.6 환경변수 접두사

| 접두사 | 용도 | 노출 |
|--------|------|------|
| `NEXT_PUBLIC_` | 브라우저 노출 | Frontend |
| `DB_` | PostgreSQL | Server only |
| `REDIS_` | Redis | Server only |
| `ML_` | AI/ML 설정 | Server only |
| `IOT_` | IoT/MQTT | Server only |
| `STORAGE_` | MinIO/S3 | Server only |
| `AUTH_` | JWT/인증 | Server only |
| `LLM_` | AI Agent LLM | Server only |

---

## 4. React 컴포넌트 네이밍 패턴

```typescript
// 도메인 + 역할 조합
LotTree           // LOT 계층 트리
LotTracePanel     // LOT 추적 패널
WorkOrderTable    // 작업지시 테이블
WorkOrderForm     // 작업지시 폼
FValueChart       // F-value 라인 차트
CcpStatusBadge    // CCP 상태 배지
EquipmentCard     // 설비 카드
OeeGauge          // OEE 게이지 차트
XRayResultViewer  // X-Ray 결과 뷰어
HaccpCheckForm    // HACCP 점검 폼
AlertCenter       // 알림 센터
AgentChatPanel    // AI Agent 챗 패널
KpiSummaryGrid    // KPI 요약 그리드
```

## 5. Python 클래스 네이밍 패턴

```python
# Router (FastAPI)
class WorkOrderRouter   # work_order_router.py
class LotRouter         # lot_router.py

# Service (비즈니스 로직)
class WorkOrderService  # work_order_service.py
class LotTraceService   # lot_trace_service.py
class FValueService     # f_value_service.py

# Repository (DB 접근)
class WorkOrderRepository
class LotRepository

# Schema (Pydantic)
class WorkOrderCreate    # 생성 요청
class WorkOrderUpdate    # 수정 요청
class WorkOrderResponse  # 응답

# SQLAlchemy Model
class WorkOrder          # DB 테이블 매핑
class LotLineage

# ML Model
class LstmPredictor      # LSTM 예측 모델
class AutoEncoderDetector # AutoEncoder 이상감지
class XgBoostCcpClassifier
class CnnXrayClassifier
```
