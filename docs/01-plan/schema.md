# 두손푸드 AI-MES 데이터 스키마 정의

**버전**: v1.0 | **작성일**: 2026-05-04 | **단계**: Phase 1 Schema
**DB**: PostgreSQL 16 + TimescaleDB 확장

---

## 1. 공통 규칙

- 모든 PK: `UUID` (gen_random_uuid())
- 생성/수정 시각: `created_at TIMESTAMPTZ DEFAULT now()`, `updated_at TIMESTAMPTZ`
- 소프트 삭제: `deleted_at TIMESTAMPTZ NULL` (NULL = 활성)
- 코드 필드: `VARCHAR(50) UNIQUE NOT NULL`
- 상태 필드: `VARCHAR(20)` + CHECK 제약 또는 Enum

---

## 2. 사용자/권한 도메인

```sql
-- 사용자
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    hashed_pw   VARCHAR(255) NOT NULL,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('admin','manager','worker','inspector','viewer')),
    department  VARCHAR(50),         -- 생산팀, 품질팀, 자재팀 등
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ
);
```

---

## 3. 제품/BOM 도메인

```sql
-- 제품 (원자재 + 반제품 + 완제품 통합)
CREATE TABLE products (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(50) UNIQUE NOT NULL,   -- HMR001
    name        VARCHAR(200) NOT NULL,
    category    VARCHAR(20) NOT NULL CHECK (category IN ('RAW','WIP','FG')),
    unit        VARCHAR(20) NOT NULL,           -- kg, g, 개, L
    shelf_life_days INT,                        -- 완제품 유통기한
    storage_temp_min NUMERIC(5,2),              -- 보관 온도 범위
    storage_temp_max NUMERIC(5,2),
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ
);

-- BOM 헤더 (버전 관리)
CREATE TABLE boms (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id  UUID NOT NULL REFERENCES products(id),
    version     INT NOT NULL DEFAULT 1,
    valid_from  DATE NOT NULL,
    valid_to    DATE,                           -- NULL = 현재 유효
    status      VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','ACTIVE','OBSOLETE')),
    created_by  UUID REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE (product_id, version)
);

-- BOM 항목 (다단계 지원)
CREATE TABLE bom_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bom_id          UUID NOT NULL REFERENCES boms(id),
    material_id     UUID NOT NULL REFERENCES products(id),
    parent_item_id  UUID REFERENCES bom_items(id),  -- NULL = 최상위
    qty_per_unit    NUMERIC(12,4) NOT NULL,
    unit            VARCHAR(20) NOT NULL,
    loss_rate       NUMERIC(5,2) DEFAULT 0,         -- 손실률 (%)
    sequence        INT NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

---

## 4. 생산 도메인

```sql
-- 생산 라인
CREATE TABLE production_lines (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(50) UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    capacity    NUMERIC(10,2),   -- 시간당 최대 생산량
    unit        VARCHAR(20),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 공정 정의
CREATE TABLE processes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(50) UNIQUE NOT NULL,
    name            VARCHAR(100) NOT NULL,       -- 혼합, 살균, 충진, 포장
    sequence        INT NOT NULL,
    standard_time   INT,                          -- 표준 소요시간 (분)
    is_ccp          BOOLEAN DEFAULT FALSE,
    ccp_id          UUID,                         -- ccp 테이블 FK (나중에 추가)
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- 생산지시 (Work Order)
CREATE TABLE work_orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(50) UNIQUE NOT NULL,  -- WO-20261201-0001
    product_id      UUID NOT NULL REFERENCES products(id),
    bom_id          UUID NOT NULL REFERENCES boms(id),
    line_id         UUID REFERENCES production_lines(id),
    qty_target      NUMERIC(12,2) NOT NULL,
    unit            VARCHAR(20) NOT NULL,
    qty_done        NUMERIC(12,2) DEFAULT 0,
    qty_defect      NUMERIC(12,2) DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'PLANNED'
                    CHECK (status IN ('PLANNED','RELEASED','IN_PROGRESS','COMPLETED','CANCELLED')),
    scheduled_date  DATE NOT NULL,
    started_at      TIMESTAMPTZ,
    ended_at        TIMESTAMPTZ,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ
);

-- 공정 실적 기록
CREATE TABLE process_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_order_id   UUID NOT NULL REFERENCES work_orders(id),
    process_id      UUID NOT NULL REFERENCES processes(id),
    line_id         UUID REFERENCES production_lines(id),
    worker_id       UUID REFERENCES users(id),
    lot_id          UUID,                         -- lots 테이블 FK
    qty_input       NUMERIC(12,2),
    qty_output      NUMERIC(12,2),
    qty_defect      NUMERIC(12,2) DEFAULT 0,
    defect_reason   VARCHAR(200),
    started_at      TIMESTAMPTZ,
    ended_at        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

---

## 5. LOT 트레이서빌리티 도메인

```sql
-- LOT 마스터
CREATE TABLE lots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(100) UNIQUE NOT NULL,  -- DS-20261201-HMR001-0001
    type            VARCHAR(10) NOT NULL CHECK (type IN ('RAW','WIP','FG')),
    product_id      UUID NOT NULL REFERENCES products(id),
    work_order_id   UUID REFERENCES work_orders(id),  -- RAW는 NULL 가능
    supplier_id     UUID,                              -- 원자재 공급업체
    qty             NUMERIC(12,2) NOT NULL,
    unit            VARCHAR(20) NOT NULL,
    status          VARCHAR(20) DEFAULT 'ACTIVE'
                    CHECK (status IN ('ACTIVE','ON_HOLD','CONSUMED','SHIPPED','RECALLED')),
    received_at     TIMESTAMPTZ,                       -- 원자재 입고일
    produced_at     TIMESTAMPTZ,                       -- 생산일
    expiry_date     DATE,
    storage_location VARCHAR(100),
    qr_code         VARCHAR(200),
    rfid_tag        VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ
);

-- LOT 계보 (Closure Table — 다단계 부모-자식 관계)
CREATE TABLE lot_lineage (
    ancestor_lot_id     UUID NOT NULL REFERENCES lots(id),
    descendant_lot_id   UUID NOT NULL REFERENCES lots(id),
    depth               INT NOT NULL DEFAULT 0,    -- 0 = self, 1 = 직계, 2+ = 간접
    relation_type       VARCHAR(50),               -- USED_IN, TRANSFORMED_TO 등
    qty_used            NUMERIC(12,4),
    created_at          TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (ancestor_lot_id, descendant_lot_id)
);
CREATE INDEX idx_lot_lineage_descendant ON lot_lineage(descendant_lot_id);
CREATE INDEX idx_lot_lineage_ancestor ON lot_lineage(ancestor_lot_id);
```

---

## 6. 품질 도메인

```sql
-- CCP 정의
CREATE TABLE ccps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(20) UNIQUE NOT NULL,  -- CCP-1 ~ CCP-7
    name            VARCHAR(100) NOT NULL,         -- 살균 온도, 금속 검출 등
    process_id      UUID REFERENCES processes(id),
    parameter       VARCHAR(50) NOT NULL,          -- temperature, f_value, metal_size
    unit            VARCHAR(20) NOT NULL,
    limit_min       NUMERIC(10,4),
    limit_max       NUMERIC(10,4),
    monitoring_freq VARCHAR(50),                   -- 매 배치, 1시간마다 등
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT now()
);
-- processes.ccp_id FK 추가
ALTER TABLE processes ADD CONSTRAINT fk_process_ccp FOREIGN KEY (ccp_id) REFERENCES ccps(id);

-- CCP 모니터링 기록
CREATE TABLE ccp_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ccp_id          UUID NOT NULL REFERENCES ccps(id),
    work_order_id   UUID NOT NULL REFERENCES work_orders(id),
    lot_id          UUID REFERENCES lots(id),
    measured_at     TIMESTAMPTZ NOT NULL,
    measured_value  NUMERIC(10,4) NOT NULL,
    measured_by     UUID REFERENCES users(id),
    is_deviation    BOOLEAN DEFAULT FALSE,
    corrective_action TEXT,
    photo_urls      TEXT[],
    verified_by     UUID REFERENCES users(id),
    verified_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- F-value 살균 기록
CREATE TABLE f_value_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sterilizer_id   UUID NOT NULL,                 -- 살균기 equipment id
    work_order_id   UUID NOT NULL REFERENCES work_orders(id),
    lot_id          UUID REFERENCES lots(id),
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ,
    f0_target       NUMERIC(8,4),                  -- 목표 F값
    f0_calculated   NUMERIC(8,4),                  -- 실제 계산 F값
    is_passed       BOOLEAN,
    ai_prediction   NUMERIC(8,4),                  -- AI 예측 F값
    ai_confidence   NUMERIC(5,4),
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- F-value 온도 시계열 (TimescaleDB Hypertable)
CREATE TABLE f_value_temperature_series (
    time            TIMESTAMPTZ NOT NULL,
    f_value_record_id UUID NOT NULL REFERENCES f_value_records(id),
    temperature     NUMERIC(6,2) NOT NULL,
    pressure        NUMERIC(8,4),
    f0_accumulated  NUMERIC(8,4)
);
SELECT create_hypertable('f_value_temperature_series', 'time');

-- X-Ray 이물 검출 결과
CREATE TABLE xray_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_id      UUID NOT NULL,                 -- X-Ray 설비 id
    work_order_id   UUID NOT NULL REFERENCES work_orders(id),
    lot_id          UUID REFERENCES lots(id),
    inspected_at    TIMESTAMPTZ NOT NULL,
    result          VARCHAR(5) NOT NULL CHECK (result IN ('OK','NG')),
    contaminant_type VARCHAR(50),                  -- metal, bone, plastic, glass
    contaminant_size NUMERIC(6,2),                 -- mm
    confidence      NUMERIC(5,4),
    image_url       VARCHAR(500),
    grad_cam_url    VARCHAR(500),
    ai_classification VARCHAR(50),
    reviewed_by     UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

---

## 7. 설비 도메인

```sql
-- 설비 마스터
CREATE TABLE equipment (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(50) UNIQUE NOT NULL,
    name            VARCHAR(200) NOT NULL,
    type            VARCHAR(50) NOT NULL,           -- STERILIZER, XRAY, FILLER, PACKING 등
    line_id         UUID REFERENCES production_lines(id),
    manufacturer    VARCHAR(100),
    model_no        VARCHAR(100),
    installed_at    DATE,
    status          VARCHAR(20) DEFAULT 'RUNNING'
                    CHECK (status IN ('RUNNING','IDLE','MAINTENANCE','FAULT','OFFLINE')),
    opc_ua_node_id  VARCHAR(200),                  -- OPC-UA 노드 경로
    mqtt_topic      VARCHAR(200),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ
);

-- 정비 기록
CREATE TABLE maintenance_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id    UUID NOT NULL REFERENCES equipment(id),
    type            VARCHAR(20) NOT NULL CHECK (type IN ('PREVENTIVE','CORRECTIVE','PREDICTIVE','EMERGENCY')),
    priority        VARCHAR(10) CHECK (priority IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    status          VARCHAR(20) DEFAULT 'REQUESTED'
                    CHECK (status IN ('REQUESTED','IN_PROGRESS','COMPLETED','CANCELLED')),
    description     TEXT,
    ai_triggered    BOOLEAN DEFAULT FALSE,          -- AI 예측 정비 여부
    ai_failure_prob NUMERIC(5,4),                  -- AI 고장 확률
    requested_at    TIMESTAMPTZ DEFAULT now(),
    started_at      TIMESTAMPTZ,
    ended_at        TIMESTAMPTZ,
    worker_id       UUID REFERENCES users(id),
    parts_replaced  JSONB,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- IoT 센서 시계열 (TimescaleDB Hypertable)
CREATE TABLE iot_sensor_readings (
    time        TIMESTAMPTZ NOT NULL,
    device_id   UUID NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,   -- vibration, current, temperature, pressure
    value       NUMERIC(12,4) NOT NULL,
    unit        VARCHAR(20),
    quality     INT DEFAULT 192,        -- OPC-UA Quality Code
    tags        JSONB
);
SELECT create_hypertable('iot_sensor_readings', 'time');
CREATE INDEX ON iot_sensor_readings (device_id, time DESC);

-- 설비 OEE 집계 (TimescaleDB 연속 집계)
CREATE MATERIALIZED VIEW equipment_oee_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    AVG(value) FILTER (WHERE sensor_type = 'availability') AS availability,
    AVG(value) FILTER (WHERE sensor_type = 'performance')  AS performance,
    AVG(value) FILTER (WHERE sensor_type = 'quality')      AS quality_rate
FROM iot_sensor_readings
GROUP BY bucket, device_id;
```

---

## 8. HACCP 도메인

```sql
-- HACCP 점검 계획
CREATE TABLE haccp_check_plans (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ccp_id      UUID NOT NULL REFERENCES ccps(id),
    frequency   VARCHAR(20) NOT NULL,  -- DAILY, PER_BATCH, HOURLY
    responsible_role VARCHAR(20),
    checklist   JSONB,                 -- 점검 항목 정의
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- HACCP 점검 기록
CREATE TABLE haccp_check_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id         UUID NOT NULL REFERENCES haccp_check_plans(id),
    work_order_id   UUID REFERENCES work_orders(id),
    checked_by      UUID NOT NULL REFERENCES users(id),
    checked_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    results         JSONB NOT NULL,    -- {item_id, value, is_pass}[]
    overall_pass    BOOLEAN NOT NULL,
    notes           TEXT,
    photo_urls      TEXT[],
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

---

## 9. 알림 도메인

```sql
CREATE TABLE notifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type        VARCHAR(30) NOT NULL,   -- CCP_DEVIATION, EQUIPMENT_FAULT, LOT_HOLD 등
    severity    VARCHAR(10) NOT NULL CHECK (severity IN ('CRITICAL','WARNING','INFO')),
    title       VARCHAR(200) NOT NULL,
    body        TEXT,
    target_role VARCHAR(20),            -- NULL = 전체
    target_user UUID REFERENCES users(id),
    ref_type    VARCHAR(50),            -- 참조 엔티티 타입
    ref_id      UUID,                   -- 참조 엔티티 ID
    is_read     BOOLEAN DEFAULT FALSE,
    read_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_notifications_target ON notifications(target_user, is_read, created_at DESC);
```

---

## 10. 인덱스 및 성능 전략

```sql
-- 자주 사용하는 조회 인덱스
CREATE INDEX idx_lots_code        ON lots(code);
CREATE INDEX idx_lots_status      ON lots(status, type);
CREATE INDEX idx_lots_product     ON lots(product_id, produced_at DESC);
CREATE INDEX idx_work_orders_status ON work_orders(status, scheduled_date);
CREATE INDEX idx_ccp_records_deviation ON ccp_records(is_deviation, measured_at DESC);
CREATE INDEX idx_xray_results_ng  ON xray_results(result, inspected_at DESC) WHERE result = 'NG';

-- LOT 계보 역추적 쿼리 (예시)
-- 완제품 LOT → 모든 원자재 LOT 역추적
SELECT l.* FROM lots l
JOIN lot_lineage ll ON ll.ancestor_lot_id = l.id
WHERE ll.descendant_lot_id = :fg_lot_id
  AND l.type = 'RAW'
ORDER BY ll.depth;

-- 원자재 LOT → 영향받은 모든 완제품 LOT 전방추적
SELECT l.* FROM lots l
JOIN lot_lineage ll ON ll.descendant_lot_id = l.id
WHERE ll.ancestor_lot_id = :raw_lot_id
  AND l.type = 'FG';
```
