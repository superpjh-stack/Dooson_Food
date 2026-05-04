# [ARCH] 두손푸드 AI-MES 시스템 아키텍처 설계서

**작성자**: Architect (Enterprise Expert)
**작성일**: 2026-05-04
**버전**: v1.0
**프로젝트**: 두손푸드 AI-MES
**단계**: PDCA Design
**관련 Plan**: PM1, PM2, PM3
**관련 UI**: UI1, UI2, UI3

---

## 0. 문서 목적

이 문서는 두손푸드 AI-MES 시스템의 전체 기술 아키텍처를 정의함:
1. 전체 시스템 아키텍처 다이어그램
2. 기술 스택 선정 근거
3. 데이터 모델 (주요 ERD)
4. API 설계 원칙
5. AI/ML 파이프라인 아키텍처
6. IoT/PLC 연동 방식
7. 배포 아키텍처

대상 독자: CTO, 백엔드/프론트엔드/ML 엔지니어, DevOps 팀

---

## 1. 전체 시스템 아키텍처

### 1.1 컨텍스트 다이어그램 (Layered View)

```
                        ┌──────────────────────────────────┐
                        │       사용자 / Channel             │
                        │  공장장 / 부서장 / 작업자 / 점검자 │
                        └──────────────────────────────────┘
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                              ▼
+------------------+         +------------------+          +------------------+
|  Web App (PC)    |         |  Tablet (현장)   |          |  Mobile (점검)   |
|  Next.js 14+     |         |  Next.js PWA     |          |  Next.js PWA     |
|  대시보드/관리    |         |  작업자/X-Ray   |          |  HACCP/정비 일지 |
+------------------+         +------------------+          +------------------+
        │                            │                              │
        └────────────┬───────────────┴──────────────┬───────────────┘
                     │                              │
                     ▼                              ▼
              +-------------------+        +-------------------+
              |  API Gateway      |◀──────▶|  WebSocket Hub    |
              |  (NGINX + Auth)   |        |  (Socket.io)      |
              |  REST + GraphQL   |        |  실시간 알림/차트 |
              +-------------------+        +-------------------+
                     │                              │
   ┌──────┬──────────┼──────────┬─────────┐         │
   ▼      ▼          ▼          ▼         ▼         ▼
+------+ +-------+ +------+ +-------+ +-------+ +---------+
|생산  | |품질   | |HACCP | |설비   | |LOT    | |  AI     |
|서비스| |서비스 | |서비스| |서비스 | |서비스 | |  Agent  |
|FastAPI||FastAPI| |FastAPI||FastAPI||FastAPI| | Hub      |
+------+ +-------+ +------+ +-------+ +-------+ +---------+
   │      │          │         │         │         │
   └──────┴──────────┼─────────┴─────────┘         │
                     │                             │
                     ▼                             ▼
             +----------------+         +-----------------------+
             |  데이터 허브   |◀───────▶|  ML 추론 서비스         |
             |  PostgreSQL +  |         |  FastAPI + Ray Serve  |
             |  TimescaleDB + |         |  LSTM/AE/XGB/CNN       |
             |  Redis + S3    |         |  RAG (LLM)             |
             +----------------+         +-----------------------+
                     │                             │
                     │                             ▼
                     │                  +-----------------------+
                     │                  |  ML 학습 Pipeline      |
                     │                  |  Airflow + MLflow      |
                     │                  |  GPU Cluster (학습용) |
                     │                  +-----------------------+
                     │
                     ▼
              +-------------------+         +-------------------+
              |  Edge IoT Gateway |◀──────▶|  PLC / Sensors    |
              |  Node-RED +       |         |  OPC-UA / Modbus |
              |  MQTT Broker      |         |  X-Ray / 살균기 |
              |  (현장 설치)      |         |  진동/온도/전류  |
              +-------------------+         +-------------------+
                     │
                     ▼
              +-------------------+
              |  ERP 연동         |
              |  REST API/RPC     |
              +-------------------+
```

### 1.2 아키텍처 스타일

- **Modular Monolith → Microservices 진화 전략**:
  - **Phase 1 (2026 Q3-Q4, MVP)**: Modular Monolith (FastAPI 1개, 도메인별 모듈)
  - **Phase 2 (2027 Q1-Q2)**: 핵심 도메인을 Microservices로 분리 (LOT, 품질, AI Agent 우선)
  - **이유**: 초기 빠른 개발 + 운영 부담 최소화 + 점진적 분리

- **이벤트 기반 통신**:
  - 도메인 간 비동기 이벤트(Kafka 또는 Redis Streams)
  - 예: `lot.created`, `ccp.deviated`, `equipment.anomaly_detected`

- **CQRS 부분 도입**:
  - 쓰기: 도메인 모델 (PostgreSQL)
  - 읽기 (대시보드): TimescaleDB (시계열) + Redis (캐시)

---

## 2. 기술 스택 선정 및 근거

### 2.1 프론트엔드

| 기술 | 선정 이유 | 비고 |
|------|---------|------|
| **Next.js 14+ (App Router)** | SSR/SSG/CSR 혼합, 풀스택 개발, RSC로 초기 로딩 최적화 | TypeScript 강제 |
| **TypeScript** | 타입 안정성, 대규모 프로젝트 유지보수 | strict mode |
| **Tailwind CSS** | 디자인 토큰 일관성, 빠른 개발 | shadcn/ui와 호환 |
| **shadcn/ui** | 커스터마이징 자유도, 한국어 친화적 | Radix UI 기반 |
| **Recharts + Visx** | 대시보드 차트, React 친화적 | 대용량은 ECharts |
| **TanStack Query** | 서버 상태 관리, 자동 캐싱/리페치 | WebSocket과 결합 |
| **Zustand** | 클라이언트 상태 (UI 상태) | Redux 대비 단순 |
| **react-hook-form + zod** | 폼 검증 (작업 지시, BOM 등) | 백엔드 스키마 공유 |
| **Socket.io Client** | 실시간 알림/차트 | reconnect 자동 |
| **PWA (next-pwa)** | 모바일 오프라인 모드 | 작업자 태블릿 필수 |

### 2.2 백엔드

| 기술 | 선정 이유 | 비고 |
|------|---------|------|
| **Python 3.12 + FastAPI** | AI/ML 통합 용이, 비동기 지원, 빠른 개발 | OpenAPI 자동 문서 |
| **SQLAlchemy 2.0 (async)** | ORM, async/await | Alembic 마이그레이션 |
| **Pydantic v2** | 검증, 직렬화 | FastAPI 통합 |
| **Celery + Redis** | 비동기 작업 (보고서 생성, 알림 발송) | Beat 스케줄러 |
| **APScheduler** | 정기 작업 (KPI 집계, 모델 재학습) | 단순 |
| **Node.js (선택)** | WebSocket Hub만 (Socket.io 안정성) | Python+FastAPI WS도 가능 |

**Python vs Node.js 결정**: AI/ML 라이브러리(LSTM, XGBoost, CNN, LangChain) 통합 필요성으로 **Python FastAPI 우선**, WebSocket은 동일 스택 유지.

### 2.3 데이터 저장

| 저장소 | 용도 | 선정 이유 |
|------|------|---------|
| **PostgreSQL 16** | 트랜잭션 데이터 (LOT, BOM, 작업지시, HACCP 기록) | ACID, JSON 지원, RLS |
| **TimescaleDB** (PG 확장) | 시계열 데이터 (IoT 센서, F-value, 진동, OEE) | 압축, 자동 파티셔닝, 연속 집계 |
| **Redis 7** | 캐시, Pub/Sub, Celery Broker | 고성능, 다용도 |
| **MinIO (또는 S3)** | 이미지 (X-Ray DICOM), 보고서 PDF, AI 학습 데이터 | 5년+ 보관, 라이프사이클 |
| **Qdrant (또는 pgvector)** | RAG 벡터 임베딩 (식약처 고시, SOP) | 식품 법규 검색 |
| **Apache Kafka (선택, Phase 2)** | 도메인 이벤트 버스 | 도메인 간 비동기 |

### 2.4 AI/ML

| 기술 | 용도 |
|------|------|
| **PyTorch 2.x** | LSTM, AutoEncoder, CNN 학습/추론 |
| **XGBoost** | CCP 분류 |
| **scikit-learn** | 전처리, 보조 모델 |
| **MLflow** | 모델 버전 관리, Tracking |
| **DVC** | 학습 데이터 버전 관리 |
| **Ray Serve** | 모델 서빙 (스케일 아웃) |
| **LangChain / LangGraph** | AI Agent 오케스트레이션 |
| **OpenAI / Anthropic API + Solar (한국어)** | LLM (선택 가능) |
| **Sentence-Transformers** | 임베딩 (RAG) |
| **Apache Airflow** | 학습 파이프라인 스케줄러 |

### 2.5 IoT/PLC

| 기술 | 용도 |
|------|------|
| **OPC-UA Server** | PLC 표준 인터페이스 (살균기, 충진기 등) |
| **Modbus TCP** | 레거시 PLC 대응 |
| **MQTT (Eclipse Mosquitto)** | IoT 센서 메시지 브로커 |
| **Node-RED** | 엣지 데이터 가공/라우팅 (No-code) |
| **InfluxDB Edge (선택)** | 엣지 로컬 캐시 (오프라인 대응) |

### 2.6 인프라/DevOps

| 기술 | 용도 |
|------|------|
| **Docker / Docker Compose** | 로컬 개발, 단일 노드 배포 |
| **Kubernetes (K3s)** | 프로덕션 (경량) |
| **NGINX** | API Gateway, Load Balancer |
| **GitHub Actions** | CI/CD |
| **Sentry** | 에러 모니터링 |
| **Prometheus + Grafana** | 메트릭 모니터링 |
| **Loki** | 로그 집계 |

**클라우드 vs 온프레미스**: 식품 제조 데이터(특히 HACCP 기록)의 보안 민감도와 공장 내 통신 안정성을 고려하여 **하이브리드(Hybrid) 권장**:
- **온프레미스 (공장 내)**: IoT Gateway, Edge ML 추론, 시계열 캐시
- **클라우드 (AWS/Azure)**: 학습용 GPU, 백업, 분석 DW
- **VPN/전용선**: 양방향 동기화

---

## 3. 데이터 모델 (주요 ERD)

### 3.1 핵심 도메인 엔티티

```
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│   Product      │ 1────∞│      BOM       │ 1────∞│  BOMItem       │
│ ─────────────  │       │ ─────────────  │       │ ─────────────  │
│ id (PK)        │       │ id (PK)        │       │ id (PK)        │
│ code           │       │ product_id (FK)│       │ bom_id (FK)    │
│ name           │       │ version        │       │ material_id    │
│ category       │       │ valid_from     │       │ qty_per_unit   │
│ unit           │       │ valid_to       │       │ unit           │
└────────────────┘       │ status         │       │ loss_rate      │
                         │ created_by     │       │ alternatives[] │
                         └────────────────┘       └────────────────┘

┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│  WorkOrder     │ 1────∞│ ProcessRecord  │ ∞────1│   Process      │
│ ─────────────  │       │ ─────────────  │       │ ─────────────  │
│ id (PK)        │       │ id (PK)        │       │ id (PK)        │
│ code (UQ)      │       │ wo_id (FK)     │       │ name           │
│ product_id     │       │ process_id (FK)│       │ sequence       │
│ bom_version    │       │ line_id        │       │ standard_time  │
│ qty_target     │       │ start_time     │       │ ccp_id (옵션)  │
│ qty_done       │       │ end_time       │       └────────────────┘
│ qty_defect     │       │ qty_good       │
│ status         │       │ qty_defect     │
│ scheduled_at   │       │ defect_reason  │
│ started_at     │       │ worker_id      │
│ ended_at       │       └────────────────┘
└────────────────┘                ▲
        │                         │
        │ 1                       │ ∞
        ▼                         │
┌────────────────────────┐        │
│        Lot              │────────┤
│ ─────────────────────── │
│ id (PK)                 │
│ code (UQ)               │
│ type (RAW/WIP/FG)       │
│ product_id              │
│ qty                     │
│ unit                    │
│ wo_id (FK, NULL if RAW) │
│ parent_lot_ids[] (FK)   │
│ produced_at             │
│ status (ACTIVE/HOLD/CONSUMED)│
│ x_ray_results[] (JSONB) │
│ ccp_records[] (JSONB)   │
└────────────────────────┘
        │ ∞ ↔ ∞
        ▼
┌────────────────────────┐
│   LotTraceability      │  (Materialized Path or Closure Table)
│ ─────────────────────── │
│ ancestor_lot_id (FK)   │
│ descendant_lot_id (FK) │
│ depth                   │
│ relation_type           │
└────────────────────────┘
```

### 3.2 품질 도메인

```
┌────────────────────┐       ┌────────────────────┐
│   CCP              │ 1────∞│  CCPRecord         │
│ ─────────────────  │       │ ─────────────────  │
│ id (PK)            │       │ id (PK)            │
│ code (CCP-1~7)     │       │ ccp_id (FK)        │
│ name               │       │ wo_id (FK)         │
│ description        │       │ lot_id (FK)        │
│ threshold_min      │       │ measured_at        │
│ threshold_max      │       │ measured_value     │
│ unit               │       │ is_deviation       │
└────────────────────┘       │ corrective_action  │
                             │ photo_urls[]       │
                             └────────────────────┘

┌────────────────────┐       ┌────────────────────┐
│   FvalueRecord     │       │   XRayResult        │
│ ─────────────────  │       │ ─────────────────  │
│ id (PK)            │       │ id (PK)            │
│ sterilizer_id      │       │ xray_machine_id    │
│ wo_id (FK)         │       │ wo_id (FK)         │
│ lot_id (FK)        │       │ lot_id (FK)        │
│ start_time         │       │ inspected_at       │
│ end_time           │       │ result (OK/NG)     │
│ f0_calculated      │       │ contaminant_type   │
│ temperature_series │       │ confidence         │
│   (TimescaleDB)    │       │ image_url (S3)     │
│ ai_prediction      │       │ ai_classification  │
│ ai_confidence      │       │ ai_grad_cam_url    │
└────────────────────┘       └────────────────────┘

┌─────────────────────────┐
│   IoTSensorReading      │  (TimescaleDB Hypertable)
│ ─────────────────────── │
│ time (PK)               │
│ device_id (PK)          │
│ sensor_type             │  (vibration, current, temp, pressure)
│ value                   │
│ unit                    │
│ tags JSONB              │
└─────────────────────────┘
```

### 3.3 설비 도메인

```
┌────────────────────┐       ┌────────────────────┐
│   Equipment        │ 1────∞│  MaintenanceRecord │
│ ─────────────────  │       │ ─────────────────  │
│ id (PK)            │       │ id (PK)            │
│ code               │       │ equipment_id (FK)  │
│ name               │       │ type (CHECK/REPAIR)│
│ type               │       │ priority           │
│ line_id            │       │ status             │
│ status             │       │ requested_at       │
│ installed_at       │       │ started_at         │
└────────────────────┘       │ ended_at           │
        │                    │ worker_id          │
        │ 1                  │ parts_used JSONB   │
        ▼                    │ photos []          │
┌────────────────────┐       │ ai_predicted       │
│   OEERecord         │      │   (AI 발행 여부)    │
│ ───────────────────│      └────────────────────┘
│ id (PK)             │
│ equipment_id (FK)   │
│ date                │
│ availability        │
│ performance         │
│ quality             │
│ oee                 │
│ runtime_min         │
│ downtime_min        │
└─────────────────────┘
```

### 3.4 사용자/권한

```
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│   User         │ ∞────∞│   Role         │ 1────∞│  Permission    │
│ ─────────────  │       │ ─────────────  │       │ ─────────────  │
│ id (PK)        │       │ id (PK)        │       │ id (PK)        │
│ email          │       │ name           │       │ resource       │
│ name           │       │ description    │       │ action (R/W)   │
│ employee_id    │       └────────────────┘       └────────────────┘
│ department_id  │
│ phone          │       Roles: 공장장, 생산팀장, 품질팀장, 설비팀장,
│ active         │              자재팀장, 작업자, HACCP 점검자, 정비공
└────────────────┘
```

### 3.5 핵심 인덱스/파티셔닝 전략

- **시계열 데이터**: TimescaleDB 자동 파티셔닝 (1일 단위), 7일 후 압축
- **LOT 추적**: Closure Table 또는 PostgreSQL `ltree` 확장 사용
- **5년 보관**: 30일 이상 데이터는 콜드 스토리지(S3 Glacier)로 자동 이관 + 인덱스 유지
- **검색 최적화**: 작업지시 코드, LOT 번호 GIN 인덱스 (Full-text)

---

## 4. API 설계 원칙

### 4.1 일반 원칙
- **REST + WebSocket 혼합**: CRUD는 REST, 실시간은 WebSocket
- **OpenAPI 3.1 스펙**: FastAPI 자동 생성, 타입 공유 가능
- **버전 관리**: URL Path (`/api/v1/...`)
- **JSON 응답 표준**:
  ```json
  {
    "success": true,
    "data": {...},
    "error": null,
    "meta": { "page": 1, "total": 100 }
  }
  ```

### 4.2 인증/인가
- **Auth**: JWT (Access 15분 + Refresh 7일)
- **OAuth 2.0**: ERP 연동 시
- **RBAC**: Role 기반 미들웨어 (FastAPI Depends)
- **RLS (Row Level Security)**: PostgreSQL RLS로 부서별 데이터 격리 (선택)

### 4.3 주요 API 엔드포인트 (예시)

```
# 생산 도메인
POST   /api/v1/production/work-orders        # 작업 지시 발행
GET    /api/v1/production/work-orders        # 목록 조회
GET    /api/v1/production/work-orders/{id}   # 상세 조회
PATCH  /api/v1/production/work-orders/{id}   # 부분 수정
POST   /api/v1/production/work-orders/{id}/start  # 공정 시작
POST   /api/v1/production/work-orders/{id}/complete

# LOT 도메인
POST   /api/v1/lots                          # LOT 생성
GET    /api/v1/lots/{code}                   # 조회
GET    /api/v1/lots/{code}/trace?direction=forward|backward  # 추적
POST   /api/v1/lots/recall-simulation        # 회수 시뮬레이션

# BOM 도메인
GET    /api/v1/products/{id}/bom?version={v}  # BOM 조회
POST   /api/v1/products/{id}/bom              # 신규 BOM 버전 발행
GET    /api/v1/products/{id}/bom/diff?from=v3.1&to=v3.2

# 품질 도메인
GET    /api/v1/quality/ccp/records           # CCP 기록 조회
POST   /api/v1/quality/ccp/records           # CCP 기록 추가 (모바일)
GET    /api/v1/quality/fvalue/{sterilizer_id}/realtime  # WS 별도
GET    /api/v1/quality/xray/{machine_id}/results
POST   /api/v1/quality/corrective-actions    # 시정조치 발행

# 설비 도메인
GET    /api/v1/equipment                     # 설비 목록
GET    /api/v1/equipment/{id}/oee?period=day|week|month
GET    /api/v1/equipment/{id}/sensors/{sensor}?from={ts}&to={ts}
POST   /api/v1/equipment/{id}/maintenance    # 정비 요청

# AI Agent
POST   /api/v1/ai/agent/query                # 자연어 질의
GET    /api/v1/ai/agent/sessions/{id}/history
POST   /api/v1/ai/insights/generate          # 인사이트 생성

# KPI
GET    /api/v1/kpi/summary                   # 4대 KPI
GET    /api/v1/kpi/{type}?period=...&granularity=hour|day|week
POST   /api/v1/kpi/reports                   # 보고서 생성

# WebSocket Endpoints
WS     /ws/alerts                            # 실시간 알림
WS     /ws/quality/fvalue/{sterilizer_id}    # F-value 스트림
WS     /ws/equipment/{id}/sensors            # 센서 스트림
WS     /ws/production/lines                  # 라인 상태 스트림
```

### 4.4 에러 처리
- HTTP 상태코드 표준 사용 (400/401/403/404/409/422/500)
- 비즈니스 에러는 `code` 필드 추가:
  ```json
  { "success": false, "error": { "code": "BOM_VERSION_CONFLICT", "message": "..." }}
  ```

### 4.5 Idempotency / 동시성
- 작업 지시 발행 등 중요 POST에 `Idempotency-Key` 헤더 지원
- LOT/BOM 등 동시 수정에 Optimistic Locking (`updated_at` 또는 `version` 컬럼)

### 4.6 Rate Limiting
- 사용자별 분당 100 req
- AI Agent 호출은 분당 30 req (LLM 비용 보호)

---

## 5. AI/ML 파이프라인 아키텍처

### 5.1 학습 파이프라인 (오프라인)

```
[원본 데이터 (PG/TSDB/S3)]
        │
        ▼
[데이터 추출 + DVC 버전관리]
        │
        ▼
[전처리 + Feature Engineering] (Airflow DAG)
        │
        ▼
[모델 학습 (PyTorch/XGBoost)]   ← GPU Cluster (A100, V100)
        │
        ▼
[검증 (Hold-out, CV) + 평가]
        │
        ▼
[MLflow Tracking → Model Registry]
        │
        ▼
[A/B 테스트 (Shadow Mode)]
        │
        ▼
[프로덕션 승격 (Production Tag)]
        │
        ▼
[Ray Serve 배포 (Rolling Update)]
```

### 5.2 추론 아키텍처 (온라인)

```
[현장 IoT 센서] ──MQTT──▶ [Edge Gateway (Node-RED)]
                                 │
                                 ├─▶ [Edge Inference] (경량 모델)
                                 │       └─▶ 즉시 알림 (지연 ≤ 100ms)
                                 │
                                 └─▶ [중앙 ML 추론 (Ray Serve)]
                                         ├─▶ LSTM (F-value, 진동 시계열 예측)
                                         ├─▶ AutoEncoder (이상 감지)
                                         ├─▶ XGBoost (CCP 분류)
                                         └─▶ CNN (X-Ray 이물 분류)
                                                 │
                                                 ▼
                                         [예측 결과 → DB + 알림]
```

### 5.3 RAG 아키텍처 (HACCP 법규 검색)

```
[식약처 고시/식품위생법 PDF/HTML]
        │ 주 1회 크롤링
        ▼
[문서 파싱 + 청킹 (LangChain)]
        │
        ▼
[Embedding (Sentence-Transformers/Solar)]
        │
        ▼
[Qdrant 벡터 DB 저장]
        │
        ▼
[사용자 질의]
        │
        ▼
[Embedding → Qdrant 유사도 검색 (Top-K=5)]
        │
        ▼
[LLM에 Context + Query 전달 (LangChain)]
        │
        ▼
[답변 + 출처 인용]
```

### 5.4 AI Agent 오케스트레이션 (LangGraph)

```
[사용자 질의: "오늘 살균기 #2 OEE 어때?"]
        │
        ▼
[Orchestrator LLM (Function Calling)]
        │
        ├─▶ [생산 Agent Tool]   ─▶ /api/production/...
        ├─▶ [품질 Agent Tool]   ─▶ /api/quality/...
        ├─▶ [HACCP Agent Tool]  ─▶ RAG + /api/haccp/...
        ├─▶ [설비 Agent Tool]   ─▶ /api/equipment/oee/...  ✅ (이 케이스)
        │
        ▼
[결과 통합 + 응답 생성]
        │
        ▼
[출처 표시 + Confidence + 답변]
```

### 5.5 모델 거버넌스

| 항목 | 정책 |
|------|------|
| 학습 데이터 | DVC 버전 관리, S3 보관 |
| 모델 | MLflow Model Registry (Staging/Production) |
| 배포 | Shadow Mode (1주) → Canary (10%) → 100% |
| 모니터링 | Prediction Drift, Feature Drift 자동 감지 |
| 재학습 | LSTM/AE 월 1회, XGBoost/CNN 분기 1회, RAG 주 1회 |
| 롤백 | 정확도 임계값 (예: F1 < 0.85) 미달 시 자동 |
| 감사 | 모든 추론 결과 + 입력 + 출력 로깅 (5년) |

### 5.6 LLM 비용 관리

- **RAG 우선**: 가능한 답변은 RAG로 처리, LLM은 자연어 생성에만
- **Caching**: 자주 반복되는 질의는 Redis 캐시 (1시간)
- **모델 라우팅**:
  - 단순 질의 → 한국어 특화 경량 모델 (Solar / HyperCLOVA X)
  - 복잡 분석 → GPT-4o / Claude 3.5
  - 영업 비밀 데이터 → 자체 호스팅 (Llama 3 / Qwen 2.5)
- **토큰 모니터링**: 사용자/도메인별 토큰 사용량 대시보드

---

## 6. IoT/PLC 연동 방식

### 6.1 통신 프로토콜

| 장비 | 프로토콜 | 비고 |
|------|---------|------|
| 살균기 (현대) | OPC-UA | 표준 |
| 충진기/밀봉기 | Modbus TCP | 레거시 대응 |
| X-Ray 검사기 | TCP/IP (벤더 사양) | Adapter 필요 |
| 진동 센서 | MQTT | 외장 IoT 센서 |
| 온도/습도 | MQTT | LoRaWAN 또는 Wi-Fi |

### 6.2 Edge Gateway 아키텍처

```
공장 내부망 (보안)
┌──────────────────────────────────────────────────────┐
│                                                       │
│  [PLC #1] ──┐                                        │
│  [PLC #2] ──┼──▶ [OPC-UA Server]                    │
│  [PLC #3] ──┘                                        │
│                                                       │
│  [센서 #1] ──┐                                        │
│  [센서 #2] ──┼──▶ [MQTT Broker (Mosquitto)]          │
│  [센서 #N] ──┘                                        │
│                                                       │
│  [X-Ray 1/2] ──▶ [Custom Adapter (Python)]           │
│                                                       │
│              │                                        │
│              ▼                                        │
│      [Edge Gateway: Node-RED]                        │
│      ├─ 로컬 캐시 (InfluxDB Edge)                    │
│      ├─ 통신 두절 시 큐잉                             │
│      └─ 데이터 정규화/변환                            │
│              │                                        │
│              ▼                                        │
│      [중앙 서버 전송 (HTTPS / MQTT TLS)]             │
└──────────────────────────────────────────────────────┘
                  │ VPN/전용선
                  ▼
        [중앙 데이터 허브]
```

### 6.3 데이터 수집 주기

| 데이터 | 주기 | 저장 |
|------|------|------|
| 진동 (스펙트럼) | 1초 | TimescaleDB (10s 압축) |
| 전류, 온도, 압력 | 1초 | TimescaleDB |
| F-value 온도 | 1초 | TimescaleDB |
| X-Ray 결과 | 이벤트 | PostgreSQL + S3 (이미지) |
| OEE | 1분 (집계) | TimescaleDB |
| 작업 실적 | 이벤트 | PostgreSQL |

### 6.4 오프라인/장애 대응

- **로컬 캐싱**: Edge Gateway 24시간 분량 저장 가능
- **자동 재동기화**: 통신 복구 시 자동 전송 (시간 순서 보장)
- **이중화**: 중요 라인은 Edge Gateway 2대 (Active-Standby)
- **알림**: 통신 두절 5분 이상 시 IT/설비팀 알림

### 6.5 보안

- **세분화된 네트워크**: 공장 OT망 ↔ IT망 분리, 일방향 게이트웨이(Data Diode) 검토
- **PLC 보안**: PLC는 읽기 전용 노출 원칙, 쓰기 명령은 화이트리스트
- **인증서**: OPC-UA / MQTT 모두 TLS + 클라이언트 인증서

---

## 7. 배포 아키텍처

### 7.1 환경 구성

| 환경 | 용도 | 인프라 |
|------|------|------|
| Local | 개발 | Docker Compose |
| Dev | 통합 테스트 | K3s 단일 노드 |
| Staging | UAT, 사전 검증 | K3s 3-node, 실제와 유사 |
| Production | 운영 | K3s 5-node + GPU 노드 1대 |

### 7.2 프로덕션 배포 (하이브리드)

```
┌──────────── 클라우드 (AWS / Azure) ────────────┐
│                                                  │
│  [GPU Cluster (A100)] - ML 학습 전용              │
│  [S3 / Blob] - 백업, 학습 데이터, 콜드 스토리지   │
│  [LLM API] - GPT/Claude (선택)                    │
│  [Backup PG] - 일일 백업 (RPO 24h)                │
│  [모니터링: Sentry, CloudWatch]                  │
│                                                  │
└──────────────────────────────────────────────────┘
                  ▲
                  │ VPN / 전용선 (양방향)
                  ▼
┌──────────── 온프레미스 (공장 내) ────────────┐
│                                                │
│  [K3s Cluster] (5 nodes + GPU 1)               │
│  ├── API Servers (FastAPI) x3                  │
│  ├── ML Inference (Ray Serve) x2 (GPU)         │
│  ├── PostgreSQL (Primary + Replica)            │
│  ├── TimescaleDB                               │
│  ├── Redis Cluster                             │
│  ├── MinIO (이미지 보관)                        │
│  ├── Kafka (Phase 2)                           │
│  ├── Qdrant (벡터 DB)                          │
│  └── NGINX Ingress                             │
│                                                │
│  [Edge Gateway #1, #2] (각 라인)                │
│                                                │
└────────────────────────────────────────────────┘
```

### 7.3 CI/CD 파이프라인

```
[GitHub Push]
      │
      ▼
[GitHub Actions]
   ├── Lint (ruff, eslint)
   ├── Unit Test (pytest, vitest)
   ├── Integration Test (testcontainers)
   ├── Build Docker Image
   └── Push to Registry (Harbor 온프레미스)
      │
      ▼
[Argo CD (GitOps)]
   ├── Dev: Auto Sync
   ├── Staging: Auto Sync (PR 머지 시)
   └── Production: Manual Sync (CTO 승인)
```

### 7.4 모니터링/알림

| 도구 | 용도 |
|------|------|
| Prometheus | 메트릭 수집 (FastAPI, Postgres, K3s) |
| Grafana | 대시보드 (인프라/앱) |
| Loki | 로그 집계 |
| Sentry | 에러 트래킹 (앱 + 클라이언트) |
| AlertManager | 알림 라우팅 (슬랙/이메일/SMS) |
| Uptime Kuma | 외부 헬스체크 |

### 7.5 백업/재해복구

- **PostgreSQL**: 매일 풀백업 + WAL 아카이빙 (PITR), 14일 보관
- **TimescaleDB**: 매일 백업 + 압축 후 S3 이관
- **MinIO**: S3로 일일 동기화
- **DR**: 클라우드 보조 사이트, RPO 24h, RTO 4h

### 7.6 성능 목표

| 지표 | 목표 |
|------|------|
| API p99 응답 | ≤ 500ms (조회), ≤ 1s (변경) |
| LOT 추적 응답 | ≤ 1s (10만 LOT 기준) |
| WS 알림 지연 | ≤ 3s |
| AI 추론 (현장 모델) | ≤ 100ms |
| AI 추론 (중앙 모델) | ≤ 2s |
| 동시 사용자 | 200명 무중단 |
| 가용성 | 99.5% (월 약 3.6h 다운타임) |

---

## 8. 보안 아키텍처

### 8.1 네트워크
- 공장 OT망 ↔ IT망 분리 (방화벽)
- 모든 외부 통신 TLS 1.3
- VPN으로만 클라우드 접근

### 8.2 데이터
- 저장 시 암호화 (PostgreSQL TDE 또는 디스크 암호화)
- 식품안전 기록은 변조 방지(Append-only + 서명)
- X-Ray 이미지는 LOT 추적 가능, 외부 유출 차단
- 개인정보(작업자 이름/연락처) 별도 테이블 + 마스킹

### 8.3 인증/감사
- MFA 강제 (관리자, 품질팀장)
- 모든 중요 액션 감사 로그 (5년 보관)
- 식약처 점검 대응: 감사 로그 PDF 추출 기능

### 8.4 컴플라이언스
- 식품위생법 시행규칙 별표 17 (자가품질검사 기록 2~3년)
- HACCP 인증 기준 (5년)
- ISO 27001 (선택), GDPR (해외 거래처 시)

---

## 9. 마이그레이션 전략

### 9.1 단계별 도입 (2026 Q3 ~ 2027 Q2)

**Phase 1 (2026 Q3-Q4) — MVP**:
- 생산관리, LOT, BOM 핵심
- F-value 자동 계산 (AI 미적용)
- X-Ray LOT 연계
- HACCP 모바일 점검
- 메인 KPI 대시보드
- AI Agent (RAG + 단순 질의)

**Phase 2 (2027 Q1) — AI 고도화**:
- LSTM/AutoEncoder F-value 예측
- CNN X-Ray 이물 분류
- LSTM 설비 예측 정비
- AI Agent 오케스트레이션 완성

**Phase 3 (2027 Q2+) — 확장**:
- What-if 시뮬레이션
- AR 정비 가이드
- 음성 AI Agent
- 마이크로서비스 분리

### 9.2 데이터 마이그레이션
- 기존 종이/엑셀 LOT 기록 5년치를 디지털화 (외주 OCR + 검증)
- 마스터 데이터(제품, BOM, 거래처) 우선 정합성 확보

### 9.3 사용자 교육
- Phase 1 시작 1개월 전 교육 시작
- Train-the-Trainer 방식 (각 부서 키맨 → 팀원)
- e-Learning + 현장 실습 + 매뉴얼

---

## 10. 리스크 및 완화책

| 리스크 | 영향 | 완화책 |
|------|------|------|
| PLC/IoT 통신 장애 | High | Edge Gateway 이중화, 로컬 캐시 24h |
| AI 모델 정확도 부족 | High | 단계별 도입, 사람 검수 병행, 임계값 운영 |
| 사용자 디지털 전환 저항 | High | UX 단순화, 단계별 교육, 챔피언 양성 |
| 데이터 폭증 (5년) | Medium | TimescaleDB 압축, 콜드 스토리지 자동 이관 |
| LLM 비용 폭증 | Medium | RAG 우선, 토큰 모니터링, 자체 호스팅 옵션 |
| 식약처 디지털 기록 인정 | High | 사전 검토, 전자서명, 감사 로그 |
| 보안 침해 (랜섬웨어 등) | High | 백업 분리, OT/IT 분리, MFA, 외부 감사 |

---

## 11. 폴더 구조 (Modular Monolith → Microservices)

```
dooson-ai-mes/
├── apps/
│   ├── web/                    # Next.js 메인 (대시보드/관리)
│   ├── tablet/                 # 작업자 PWA (Next.js)
│   └── mobile/                 # 점검자 PWA (Next.js)
│
├── packages/
│   ├── ui/                     # 공용 UI (shadcn 기반)
│   ├── api-client/             # OpenAPI 자동 생성 클라이언트
│   ├── types/                  # 공유 타입
│   └── config/
│
├── services/
│   ├── api-gateway/            # NGINX 설정
│   ├── core/                   # 메인 FastAPI (Modular Monolith)
│   │   ├── modules/
│   │   │   ├── production/
│   │   │   ├── lot/
│   │   │   ├── bom/
│   │   │   ├── quality/
│   │   │   ├── haccp/
│   │   │   ├── equipment/
│   │   │   ├── kpi/
│   │   │   └── ai_agent/
│   │   ├── shared/
│   │   └── main.py
│   │
│   ├── ml-inference/           # Ray Serve 모델 서빙
│   ├── ml-training/            # Airflow DAGs
│   ├── ws-hub/                 # WebSocket Hub (Socket.io 또는 FastAPI WS)
│   └── edge-gateway/           # Node-RED 설정 (현장 배포)
│
├── infra/
│   ├── docker/                 # Dockerfile (서비스별)
│   ├── docker-compose.yml      # 로컬 개발
│   ├── k8s/                    # K3s manifests (Kustomize)
│   │   ├── base/
│   │   └── overlays/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── production/
│   └── terraform/              # 클라우드 인프라
│
├── docs/
│   ├── 01-plan/                # PM1, PM2, PM3
│   ├── 02-design/              # UI1, UI2, UI3, ARCH (이 문서)
│   ├── 03-analysis/
│   └── 04-report/
│
├── scripts/
├── .github/workflows/          # CI/CD
├── pnpm-workspace.yaml
├── turbo.json
└── CLAUDE.md
```

---

## 12. 다음 단계

1. CTO 아키텍처 리뷰
2. 기술 스택 PoC (특히 LLM 운영 비용, IoT 인프라)
3. Phase 1 스프린트 백로그 작성 (Do 단계)
4. 데이터 모델 SQL 마이그레이션 스크립트 작성
5. OpenAPI 스펙 초안 + Mock 서버 구축
6. 보안 검토 (외부 감사관 또는 자체 보안팀)

**승인 요청**: CTO Lead

---

## 부록 A. 주요 의사결정 (ADR Style)

| ADR # | 결정 | 대안 | 근거 |
|------|------|------|------|
| 001 | Modular Monolith from MVP | 처음부터 MSA | 운영 부담 ↓, 빠른 개발, Phase 2에서 분리 |
| 002 | Python FastAPI | Node.js / Go | AI/ML 통합, FastAPI 성능 충분 |
| 003 | TimescaleDB | InfluxDB | PostgreSQL 호환성, 단일 DB 운영 |
| 004 | 하이브리드 클라우드 | 풀 클라우드 / 온프렘 | 식품 데이터 보안 + ML 비용 균형 |
| 005 | Next.js 3개 앱 분리 | 단일 Next.js | 디바이스별 UX 최적화 |
| 006 | LangGraph for AI Agent | Custom orchestration | 검증된 패턴, 빠른 개발 |
| 007 | OPC-UA 우선 | 제조사별 Adapter | 표준화, 미래 확장성 |
| 008 | K3s on-prem | Full K8s / Docker Swarm | 경량 + 표준 호환 |
