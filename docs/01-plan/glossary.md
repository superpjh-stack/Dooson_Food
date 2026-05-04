# 두손푸드 AI-MES 용어 사전 (Glossary)

**버전**: v1.0 | **작성일**: 2026-05-04 | **단계**: Phase 1 Schema

---

## 1. 비즈니스 용어 (Business Terms)

| 한국어 | English (코드명) | 정의 | 글로벌 표준 매핑 |
|--------|----------------|------|----------------|
| 생산지시 | WorkOrder | 특정 제품을 특정 수량·일정에 따라 생산하도록 내리는 지시 단위 | Manufacturing Order, Production Order |
| 작업지시 | WorkOrderLine | 생산지시를 라인/공정별로 분할한 하위 단위 | Work Order Line |
| LOT | Lot | 동일 조건에서 생산된 추적 가능한 최소 배치 단위 | Batch, Lot Number |
| 원자재 LOT | RawLot | 협력사에서 입고된 원자재의 LOT (type=RAW) | Raw Material Lot |
| 반제품 LOT | WipLot | 중간 공정을 통과한 LOT (type=WIP) | Work-In-Process Lot |
| 완제품 LOT | FgLot | 최종 포장·출하 단위 LOT (type=FG) | Finished Goods Lot |
| LOT 역추적 | LotBackTrace | 완제품 LOT → 사용 원자재 LOT를 거슬러 올라가는 조회 | Backward Traceability |
| LOT 전방추적 | LotForwardTrace | 원자재 LOT → 파생된 완제품 LOT 조회 | Forward Traceability |
| LOT 계보 | LotLineage | 부모-자식 LOT 관계 전체 그래프 | Lot Genealogy, Lot Hierarchy |
| 자재명세서 | BOM | 제품 1단위 생산에 필요한 원자재·반제품 목록과 수량 | Bill of Materials |
| 공정 | Process | 제품 생산의 순차적 작업 단계 (혼합→살균→충진→포장 등) | Process Step, Operation |
| 살균 | Sterilization | 고온·고압으로 미생물을 사멸시키는 식품 안전 공정 | Thermal Processing |
| F값 (F-value) | FValue | 살균 효과를 나타내는 적산 열량 지수 (단위: 분, 기준온도 121.1°C) | F0 Value, Sterilization Value |
| CCP | Ccp | 식품 안전 위해 요소를 제어하는 중요관리점 | Critical Control Point |
| CCP 이탈 | CcpDeviation | CCP 모니터링 값이 기준 범위를 벗어난 상태 | CCP Deviation |
| 시정조치 | CorrectiveAction | CCP 이탈 발생 시 취하는 즉각적 조치 | Corrective Action |
| 이물 검출 | ForeignBodyDetection | X-Ray로 제품 내 이물질을 탐지하는 검사 공정 | Foreign Matter Detection |
| 설비 OEE | OEE | 설비 종합 효율 = 가동률 × 성능률 × 품질률 | Overall Equipment Effectiveness |
| 예측 정비 | PredictiveMaintenance | AI 모델로 설비 고장을 사전 예측하여 수행하는 정비 | Predictive Maintenance (PdM) |
| 이상감지 | AnomalyDetection | 정상 패턴에서 벗어난 신호를 자동 탐지하는 AI 기능 | Anomaly Detection |
| HACCP | Haccp | 식품 위해요소 중점 관리 기준 (식약처 의무 인증) | Hazard Analysis Critical Control Point |
| 한계기준 | CriticalLimit | CCP에서 허용되는 최소·최대값 (예: 살균 온도 ≥ 121°C) | Critical Limit |
| 검증 | Verification | HACCP 시스템이 올바르게 작동하는지 확인하는 활동 | Verification |
| 트레이서빌리티 | Traceability | 원료 입고부터 고객 출하까지 LOT 이력을 추적하는 능력 | Traceability |
| 회수 시뮬레이션 | RecallSimulation | 문제 LOT가 영향을 미친 완제품 범위를 사전 시뮬레이션 | Recall Simulation |
| 생산 라인 | ProductionLine | 제품을 생산하는 물리적 설비 배열 단위 | Production Line |
| 작업자 | Worker | 제조 현장에서 직접 생산 작업을 수행하는 인원 | Operator |
| KPI | Kpi | 핵심 성과 지표 (생산성, 품질률, 설비 가동률 등) | Key Performance Indicator |

---

## 2. AI/ML 용어

| 한국어 | English (코드명) | 정의 |
|--------|----------------|------|
| LSTM | Lstm | Long Short-Term Memory. 시계열 데이터 예측에 사용하는 순환 신경망 |
| 오토인코더 | AutoEncoder | 입력 재구성 오차로 이상 패턴을 감지하는 비지도 학습 모델 |
| XGBoost | XgBoost | 그래디언트 부스팅 기반의 고성능 분류·회귀 모델 |
| CNN | Cnn | 이미지 특징 추출에 특화된 합성곱 신경망 (X-Ray 이물 분류) |
| RAG | Rag | 검색 증강 생성. 문서 벡터 검색 + LLM 결합으로 답변 생성 |
| AI Agent | AiAgent | 도구(Tool)를 사용해 자율적으로 목표를 달성하는 LLM 기반 에이전트 |
| Grad-CAM | GradCam | CNN이 이미지의 어느 부분을 보고 판정했는지 시각화하는 기법 |
| 신뢰도 | Confidence | AI 모델의 예측 확실성 (0~1 범위, 0.8 이상 시 고신뢰) |
| 임베딩 | Embedding | 텍스트/이미지를 벡터 공간으로 변환한 표현 (RAG에서 유사도 검색용) |
| MLflow | Mlflow | AI 모델 실험 추적·버전 관리 플랫폼 |

---

## 3. 시스템/기술 용어

| 한국어 | English | 정의 |
|--------|---------|------|
| OPC-UA | OPC-UA | PLC/설비와 통신하는 산업 표준 프로토콜 |
| MQTT | MQTT | IoT 센서 데이터 전송용 경량 메시지 브로커 프로토콜 |
| 하이퍼테이블 | Hypertable | TimescaleDB의 자동 파티셔닝 시계열 테이블 |
| Closure Table | LotLineage | 계층 구조 트리를 관계형 DB에 저장하는 패턴 (LOT 계보에 사용) |
| CQRS | CQRS | 쓰기(Command)와 읽기(Query)를 분리하는 아키텍처 패턴 |
| WebSocket | WebSocket | 실시간 양방향 통신 (대시보드 차트, 알림에 사용) |
| SSE | SSE | Server-Sent Events. 서버→클라이언트 단방향 스트리밍 |

---

## 4. 용어 사용 규칙

1. **코드**: 영어 camelCase/PascalCase 사용 (`WorkOrder`, `lotLineage`)
2. **DB 컬럼**: 영어 snake_case 사용 (`work_order_id`, `f_value_record`)
3. **API 응답**: 영어 snake_case (`lot_id`, `ccp_deviation`)
4. **UI/문서**: 한국어 우선 (생산지시, LOT 역추적)
5. **LOT 코드 형식**: `{공장코드}-{날짜}-{제품코드}-{일련번호}` 예: `DS-20261201-HMR001-0001`
6. **작업지시 코드 형식**: `WO-{YYYYMMDD}-{4자리순번}` 예: `WO-20261201-0001`
