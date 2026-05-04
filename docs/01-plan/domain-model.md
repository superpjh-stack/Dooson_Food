# 두손푸드 AI-MES 도메인 모델

**버전**: v1.0 | **작성일**: 2026-05-04 | **단계**: Phase 1 Schema

---

## 1. 도메인 맵 (전체 관계)

```
┌─────────────────────────────────────────────────────────────────┐
│                      두손푸드 AI-MES 도메인                      │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  사용자   │    │  제품/BOM │    │  생산관리 │    │ LOT추적  │  │
│  │ (Auth)   │    │(Product) │    │(Production│    │(Lot)    │  │
│  └────┬─────┘    └────┬─────┘    └────┬──────┘    └────┬─────┘  │
│       │               │               │                │         │
│       └───────────────┼───────────────┘                │         │
│                       │                                │         │
│  ┌────────────────────┼────────────────────────────────┘         │
│  │                    ▼                                           │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐                │
│  │  │  품질관리 │    │  설비관리 │    │  HACCP   │                │
│  │  │(Quality) │    │(Equipment│    │(FoodSafety│               │
│  │  └────┬─────┘    └────┬─────┘    └────┬──────┘               │
│  │       │               │               │                       │
│  │       └───────────────┼───────────────┘                       │
│  │                       │                                       │
│  │                       ▼                                       │
│  │              ┌──────────────┐    ┌──────────────┐            │
│  │              │  AI Agent Hub │    │  KPI/알림    │            │
│  │              │  (AI Domain) │    │  (Insight)   │            │
│  │              └──────────────┘    └──────────────┘            │
│  └───────────────────────────────────────────────────────────────│
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 핵심 도메인 상세

### 2.1 제품/BOM 도메인

```
Product (제품)
├── category: RAW | WIP | FG
├── 1:N → BOM (자재명세서)
│          ├── version (버전 관리)
│          ├── valid_from / valid_to (유효기간)
│          └── 1:N → BomItem (BOM 항목)
│                     ├── material: Product (재귀 참조)
│                     ├── qty_per_unit (소요량)
│                     └── parent_item_id (다단계 BOM 지원)
```

**핵심 규칙**:
- BOM은 버전 단위로 관리. 한 시점에 제품당 `ACTIVE` BOM은 1개.
- 진행 중인 WorkOrder의 BOM은 변경 불가. 신규 WorkOrder부터 적용.
- BOM 변경 시 `valid_to` 설정 후 신규 버전 생성.

---

### 2.2 생산 도메인

```
WorkOrder (생산지시)
├── product_id → Product
├── bom_id → BOM (확정 시점 BOM 버전 고정)
├── line_id → ProductionLine
├── status: PLANNED → RELEASED → IN_PROGRESS → COMPLETED
└── 1:N → ProcessRecord (공정 실적)
           ├── process_id → Process
           ├── worker_id → User
           ├── lot_id → Lot (생산된 LOT)
           ├── qty_input / qty_output / qty_defect
           └── started_at / ended_at
```

**핵심 규칙**:
- WorkOrder 상태가 `RELEASED`여야 현장 작업 시작 가능.
- 각 공정 완료 시 `ProcessRecord` 자동 생성 + LOT 연결.
- 불량 수량(`qty_defect`) 기록 시 품질팀 자동 알림.

---

### 2.3 LOT 트레이서빌리티 도메인

```
Lot (LOT 단위)
├── type: RAW → WIP → FG
├── code: DS-{날짜}-{제품코드}-{순번}
├── status: ACTIVE | ON_HOLD | CONSUMED | SHIPPED | RECALLED
└── LotLineage (Closure Table)
    ├── ancestor_lot_id (조상 LOT)
    ├── descendant_lot_id (자손 LOT)
    ├── depth (0=자신, 1=직계, 2+=간접)
    └── qty_used (소비 수량)
```

**LOT 생성 흐름**:
```
원자재 입고
    → Lot (type=RAW) 생성
    → LotLineage self row (ancestor=self, descendant=self, depth=0)

공정 투입 (RAW → WIP)
    → 새 Lot (type=WIP) 생성
    → LotLineage: (RAW→WIP, depth=1) + (self rows)

완제품 생산 (WIP → FG)
    → 새 Lot (type=FG) 생성
    → LotLineage: (WIP→FG, depth=1) + (RAW→FG, depth=2) + (self rows)
```

**역추적 쿼리 시간 목표**: 완제품 LOT → 전체 원자재 LOT, **5초 이내** (인덱스 활용).

---

### 2.4 품질 도메인

```
CCP (중요관리점)
├── code: CCP-1 ~ CCP-7
├── parameter: temperature | f_value | metal_size | ...
├── limit_min / limit_max (한계기준)
└── 1:N → CcpRecord (모니터링 기록)
           ├── is_deviation: True/False
           └── corrective_action (시정조치)

FValueRecord (F-value 살균 기록)
├── sterilizer_id → Equipment
├── f0_target / f0_calculated
├── ai_prediction (LSTM 예측값)
└── 1:N → FValueTemperatureSeries (TimescaleDB)
           └── time, temperature, pressure, f0_accumulated

XRayResult (X-Ray 이물 검출)
├── result: OK | NG
├── contaminant_type: metal | bone | plastic | glass
├── confidence (CNN 신뢰도)
└── grad_cam_url (판정 근거 시각화)
```

**품질 알림 트리거**:
| 이벤트 | 심각도 | 대상 |
|-------|--------|------|
| CCP 이탈 | CRITICAL | 품질팀장, 생산팀장 |
| F-value 미달 예측 (AI) | WARNING | 살균 담당자 |
| X-Ray NG 연속 3회 | WARNING | 품질팀 |
| X-Ray NG LOT 발생 | CRITICAL | 품질팀장 |

---

### 2.5 설비 도메인

```
Equipment (설비)
├── type: STERILIZER | XRAY | FILLER | PACKING | MIXER | ...
├── status: RUNNING | IDLE | MAINTENANCE | FAULT | OFFLINE
├── opc_ua_node_id (OPC-UA 연동)
├── mqtt_topic (MQTT 연동)
└── 1:N → MaintenanceRecord (정비 기록)
           ├── type: PREVENTIVE | CORRECTIVE | PREDICTIVE | EMERGENCY
           ├── ai_triggered (AI 예측 정비 여부)
           └── ai_failure_prob (고장 확률)

IotSensorReading (TimescaleDB Hypertable)
├── device_id → Equipment
├── sensor_type: vibration | current | temperature | pressure
└── value, unit, quality

EquipmentOeeHourly (연속 집계 뷰)
├── availability (가동률)
├── performance (성능률)
└── quality_rate (품질률)
    → OEE = 가동률 × 성능률 × 품질률
```

**AI 예측 정비 기준**:
- LSTM 모델이 30분 ~ 24시간 내 이상 패턴 감지
- AutoEncoder 재구성 오차 > 임계값 → FAULT 예측
- 고장 확률 ≥ 70% → CRITICAL 알림 + 정비 요청 자동 생성

---

### 2.6 HACCP 도메인

```
HaccpCheckPlan (점검 계획)
├── ccp_id → CCP
├── frequency: DAILY | PER_BATCH | HOURLY
└── checklist (JSONB): [{id, item, limit, unit}]

HaccpCheckRecord (점검 기록)
├── plan_id → HaccpCheckPlan
├── results (JSONB): [{item_id, value, is_pass}]
├── overall_pass
└── photo_urls[]
```

**규정 준수 요구사항**:
- HACCP 기록 최소 **2년** 보관 (식품위생법)
- CCP 모니터링 기록은 **전자서명** 필수 (식약처 전자기록 규정)
- 법규 변경 시 RAG AI Agent가 자동 검색 + 알림

---

## 3. 도메인 간 이벤트 흐름

```
WorkOrder.RELEASED
    → [알림] 현장 작업자 푸시 알림
    → [자동] BOM 기반 자재 소요량 계산

Lot.created (type=WIP/FG)
    → [자동] LotLineage 행 삽입 (Closure Table 갱신)
    → [자동] CcpRecord 생성 대기 (해당 공정이 CCP면)

CcpRecord.is_deviation = True
    → [알림 CRITICAL] 품질팀장, 생산팀장
    → [AI] HACCP AI Agent 시정조치 추천
    → [자동] Lot.status = ON_HOLD (해당 LOT 보류)

XRayResult.result = 'NG'
    → [알림 CRITICAL] 품질팀
    → [자동] Lot.status = ON_HOLD
    → [자동] 해당 WorkOrder 카운터 갱신

IotSensorReading → AI Anomaly Detection
    → 이상감지 시 → MaintenanceRecord (type=PREDICTIVE) 자동 생성
    → [알림 WARNING] 설비팀

FValueRecord.f0_calculated < f0_target
    → [알림 CRITICAL] 살균 담당자
    → [자동] Lot.status = ON_HOLD (해당 LOT 보류 필요)
```

---

## 4. API 엔티티 매핑 (주요)

| 도메인 | API 리소스 | HTTP 메서드 |
|-------|-----------|------------|
| 생산지시 | `/api/v1/work-orders` | GET, POST, PATCH |
| LOT | `/api/v1/lots` | GET, POST, PATCH |
| LOT 역추적 | `/api/v1/lots/{id}/trace/backward` | GET |
| LOT 전방추적 | `/api/v1/lots/{id}/trace/forward` | GET |
| CCP 기록 | `/api/v1/quality/ccp-records` | GET, POST |
| F-value | `/api/v1/quality/f-value-records` | GET, POST |
| X-Ray | `/api/v1/quality/xray-results` | GET, POST |
| 설비 | `/api/v1/equipment` | GET, POST, PATCH |
| IoT 데이터 | `/api/v1/equipment/{id}/sensors` | GET (WebSocket) |
| HACCP 기록 | `/api/v1/haccp/check-records` | GET, POST |
| 알림 | `/api/v1/notifications` | GET, PATCH |

---

## 5. Phase 2 확장 계획

| 현재 (Phase 1 MVP) | Phase 2 |
|-------------------|---------|
| Lot.x_ray_results[] (JSONB 컬럼) | xray_results 별도 테이블 (이미 설계 반영) |
| Redis Streams 이벤트 | Kafka 도입 (도메인 분리 시) |
| Modular Monolith | 도메인별 Microservice 분리 |
| pgvector (선택) | Qdrant 전용 클러스터 |
