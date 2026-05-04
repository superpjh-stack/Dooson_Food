# [PM2] 품질·식품안전 기획서 (F-value/CCP·X-Ray·HACCP)

**작성자**: PM2 (Product Manager - 품질/식품안전 도메인)
**작성일**: 2026-05-04
**버전**: v1.0
**프로젝트**: 두손푸드 AI-MES
**단계**: PDCA Plan
**관련 문서**: 사업계획서 v0.95 (40-43p)

---

## 1. 개요

### 1.1 배경
식품 제조업의 핵심 차별화 요소는 **식품안전(Food Safety)**과 **품질 일관성**이며, 두손푸드는 다음 세 영역에서 디지털 전환이 시급함:

1. **F-value/CCP 기반 살균 관리**: 현재 수동 측정·기록, 불량 발생 시 사후 대응만 가능
2. **X-Ray 이물 검출**: 검사기 결과는 자동이나 LOT 연계와 이물 분류는 수기
3. **HACCP/식품안전**: HACCP 7원칙 기록 모두 종이 점검표·수기 일지

### 1.2 목표
- **F-value**: LSTM + AutoEncoder 기반 30분~1일 사전 예측, 살균 효율 8~12% 향상
- **X-Ray**: CNN 기반 이물 자동 분류 + LOT Traceability 자동 연결
- **HACCP**: IoT 센서 + RAG AI Agent 기반 자동 점검·법규 검색·이상 알림

### 1.3 성공 지표
| 영역 | 지표 | AS-IS | TO-BE | 기한 |
|------|------|-------|-------|------|
| F-value | 살균 효율 | 기준값 | +10% 향상 | 2027-Q1 |
| F-value | CCP 이상 사전 예측 | 0건 | 30분~1일 전 예측 | 2027-Q1 |
| X-Ray | 이물 자동 분류 정확도 | N/A | 95% 이상 | 2027-Q1 |
| X-Ray | LOT 자동 연계율 | 0% | 100% | 2026-Q4 |
| HACCP | 점검표 디지털화율 | 0% | 100% | 2026-Q4 |
| HACCP | CCP 이상 대응 시간 | 30분 | 5분 이하 | 2027-Q1 |

---

## 2. 사용자 페르소나

### Persona Q1: 품질팀장 (윤재호, 48세, 위생사 자격)
- **역할**: 품질 정책 수립, HACCP 관리 책임자, 식약처 대응
- **Pain Point**: 식약처 점검 시 종이 기록 정리에 5일 소요, 외부 감사 시 즉시 자료 제공 어려움
- **Needs**: 통합 품질 대시보드, HACCP 자동 보고서, 법규 변경 알림

### Persona Q2: 살균 공정 담당자 (이은지, 35세)
- **역할**: 가열·살균 공정 모니터링, F-value 측정
- **Pain Point**: 측정 데이터 수기 기록·계산식 수동 입력, 이상 발생 시 늦은 대응
- **Needs**: F-value 실시간 차트, 사전 예측 알림, 자동 보고서

### Persona Q3: X-Ray 검사 담당자 (조민석, 29세)
- **역할**: X-Ray 검사기 운영, 이물 발견 시 LOT 격리
- **Pain Point**: NG 판정 후 LOT 식별·격리에 시간 소요, 이물 종류 통계 수기 정리
- **Needs**: X-Ray 자동 LOT 연계, 이물 분류 자동화, 이력 통계

### Persona Q4: HACCP 점검자 (한세영, 31세)
- **역할**: 일일 HACCP 점검, CCP 모니터링
- **Pain Point**: 종이 체크리스트, CCP 이탈 시 즉각 보고 어려움
- **Needs**: 모바일 점검 앱, 사진 첨부, 자동 알림 워크플로우

---

## 3. 사용자 스토리

### Epic 1: F-value/CCP 살균 관리 (AI 예측)
- **US-FVAL-001** (Must) — 살균 담당자로서, 살균 공정 시 F-value가 실시간 차트로 표시되고 임계값 이탈 시 즉시 알림을 받고 싶다.
- **US-FVAL-002** (Must) — 살균 담당자로서, AI가 30분~1일 전에 F-value 이상을 사전 예측하여 알려주면, 사전에 공정을 조정할 수 있다.
- **US-FVAL-003** (Must) — 품질팀장으로서, CCP 한계기준 이탈 시 자동으로 LOT 격리 워크플로우가 실행되기를 원한다.
- **US-FVAL-004** (Must) — 시스템으로서, 온도/시간 데이터로부터 F-value를 자동 계산(F0=∫10^((T-121.1)/z) dt)하여 표준 리포트로 저장한다.
- **US-FVAL-005** (Should) — 품질팀장으로서, AI 예측 정확도를 모니터링하고 모델 재학습 주기를 관리하고 싶다.
- **US-FVAL-006** (Should) — 살균 담당자로서, 과거 동일 제품의 F-value 추이와 비교하여 현재 공정의 정상성을 확인하고 싶다.

### Epic 2: X-Ray 이물 검출
- **US-XRAY-001** (Must) — 시스템으로서, X-Ray 검사기에서 OK/NG 판정 결과를 실시간 수신하여 해당 LOT에 자동 연결한다.
- **US-XRAY-002** (Must) — X-Ray 담당자로서, NG 판정 시 이물 종류(금속/유리/석/플라스틱/뼈)가 CNN으로 자동 분류되어 표시되기를 원한다.
- **US-XRAY-003** (Must) — X-Ray 담당자로서, NG 판정 즉시 해당 LOT가 자동 격리되고 후속 라인으로 흘러가지 않도록 인터록되기를 원한다.
- **US-XRAY-004** (Must) — 품질팀장으로서, 일/주/월별 이물 종류별 통계와 LOT 이력을 대시보드로 보고 싶다.
- **US-XRAY-005** (Should) — 품질팀장으로서, X-Ray 이미지를 LOT와 함께 5년 이상 보관하여 추후 분석에 활용하고 싶다.
- **US-XRAY-006** (Should) — X-Ray 담당자로서, AI 자동 분류 결과가 의심스러우면 수동 재판정하고 그 결과를 학습 데이터로 활용하고 싶다.

### Epic 3: HACCP/식품안전
- **US-HACCP-001** (Must) — HACCP 점검자로서, 모바일 앱으로 CCP/CP 점검을 수행하고 사진/측정값을 첨부하여 즉시 등록하고 싶다.
- **US-HACCP-002** (Must) — 시스템으로서, IoT 센서(온도/습도/pH)에서 CCP 임계 이탈을 자동 감지하여 즉시 알림 워크플로우를 실행한다.
- **US-HACCP-003** (Must) — 품질팀장으로서, RAG 기반 AI Agent에게 "최근 식품 살균 관련 식약처 고시 변경사항"을 자연어로 질의하고 답변과 출처를 받고 싶다.
- **US-HACCP-004** (Must) — 품질팀장으로서, HACCP 7원칙 관련 일·주·월간 리포트를 자동 생성하여 식약처 점검에 즉시 제출하고 싶다.
- **US-HACCP-005** (Should) — HACCP 점검자로서, CCP 이상 발생 시 시정조치(Corrective Action) 절차가 워크플로우로 자동 실행되기를 원한다.
- **US-HACCP-006** (Should) — 품질팀장으로서, 식품 법규(식약처 고시, 식품위생법) 변경사항을 자동 모니터링하여 알림을 받고 싶다.
- **US-HACCP-007** (Nice) — 품질팀장으로서, 외부 감사(BRC/ISO22000) 대응 시 필요 자료를 자동 패키징받고 싶다.

---

## 4. 기능 요구사항

### FR-Q1. F-value/CCP 살균 관리
| ID | 기능명 | 설명 | 우선순위 |
|----|--------|------|---------|
| FR-Q1.1 | 살균 공정 IoT 센서 데이터 수집 | 온도/시간 1초 단위 수집 | Must |
| FR-Q1.2 | F-value 자동 계산 엔진 | F0 표준 공식 적용 | Must |
| FR-Q1.3 | F-value 실시간 차트 | Trend Line + 임계 영역 | Must |
| FR-Q1.4 | LSTM 기반 시계열 예측 | 30분~1일 사전 예측 | Must |
| FR-Q1.5 | AutoEncoder 이상 감지 | 비정형 패턴 탐지 | Must |
| FR-Q1.6 | XGBoost CCP 이탈 분류 | 이탈 원인 자동 분류 | Must |
| FR-Q1.7 | 자동 LOT 격리 워크플로우 | CCP 이탈 시 인터록 | Must |
| FR-Q1.8 | 모델 정확도 모니터링 | MAE, RMSE 추적 | Should |
| FR-Q1.9 | 재학습 트리거 | 정확도 저하 시 자동 | Should |

### FR-Q2. X-Ray 이물 검출
| ID | 기능명 | 설명 | 우선순위 |
|----|--------|------|---------|
| FR-Q2.1 | X-Ray 장비 인터페이스 | OPC-UA 또는 TCP/IP | Must |
| FR-Q2.2 | OK/NG 결과 LOT 연계 | 실시간 LOT Mapping | Must |
| FR-Q2.3 | CNN 기반 이물 분류 | 5종 이상 자동 분류 | Must |
| FR-Q2.4 | NG LOT 자동 격리 인터록 | 후속 라인 차단 신호 | Must |
| FR-Q2.5 | 이물 통계 대시보드 | 일/주/월별 분석 | Must |
| FR-Q2.6 | X-Ray 이미지 보관 | 5년+ 콜드 스토리지 | Should |
| FR-Q2.7 | 수동 재판정 + 학습 피드백 | Active Learning 루프 | Should |

### FR-Q3. HACCP/식품안전
| ID | 기능명 | 설명 | 우선순위 |
|----|--------|------|---------|
| FR-Q3.1 | 모바일 HACCP 점검 앱 | 체크리스트, 사진 첨부 | Must |
| FR-Q3.2 | IoT 센서 CCP 자동 모니터링 | 온/습도/pH 실시간 | Must |
| FR-Q3.3 | RAG 기반 법규 검색 AI Agent | 식약처 고시·식품위생법 | Must |
| FR-Q3.4 | HACCP 자동 리포트 | 일/주/월 보고서 PDF | Must |
| FR-Q3.5 | 시정조치 워크플로우 | CAPA 자동 발행 | Should |
| FR-Q3.6 | 법규 변경 모니터링 | 외부 RSS/크롤링 | Should |
| FR-Q3.7 | 외부 감사 자료 패키징 | BRC/ISO22000 대응 | Nice |

### FR-Q4. 비기능 요구사항 (NFR)
- **AI 모델 정확도**:
  - F-value 예측 MAE ≤ 0.5 분
  - X-Ray 이물 분류 Accuracy ≥ 95%, F1 ≥ 0.93
  - CCP 이탈 분류 Recall ≥ 98% (False Negative 최소화)
- **성능**: 살균 데이터 수집 1초 단위, 알림 지연 ≤ 3초
- **데이터 보관**: HACCP 기록 5년+, X-Ray 이미지 5년+
- **법적 요구사항**: 식품위생법 시행규칙, HACCP 인증 기준 준수
- **데이터 무결성**: 품질 기록 변조 방지(Append-only, 전자서명)

---

## 5. AI 연동 규칙 (AI Integration Rules)

### 5.1 모델 거버넌스
| 모델 | 용도 | 입력 | 출력 | 재학습 주기 |
|------|------|------|------|-----------|
| LSTM | F-value 시계열 예측 | 온도/시간 1초 단위 시계열 | 30분~24시간 후 F-value | 월 1회 |
| AutoEncoder | F-value 이상 감지 | F-value 시계열 | 재구성 오차 (Anomaly Score) | 월 1회 |
| XGBoost | CCP 이탈 분류 | 공정 변수 (온도, 압력, 시간 등) | 이탈 카테고리 | 분기 1회 |
| CNN | X-Ray 이물 분류 | X-Ray 이미지 | 이물 종류 + Confidence | 분기 1회 |
| RAG (LLM) | HACCP 법규 검색 | 자연어 질의 | 답변 + 출처 문서 | 주 1회 (법규 업데이트) |

### 5.2 AI 결과 신뢰도 정책
- **Confidence ≥ 95%**: 자동 의사결정 (LOT 격리 등)
- **70% ≤ Confidence < 95%**: 사람 확인 후 결정
- **Confidence < 70%**: 사람 우선, AI는 보조 정보로만

### 5.3 모델 운영 (MLOps)
- 학습 데이터 버전 관리 (DVC)
- 모델 버전 관리 (MLflow Model Registry)
- A/B 테스트 후 프로덕션 승격
- Drift 모니터링 (Feature drift, Performance drift)

---

## 6. 식품 법규 요구사항

### 6.1 준수 법규
- **식품위생법** (제48조 HACCP)
- **식약처 고시 「식품 및 축산물 안전관리인증기준」**
- **식품위생법 시행규칙 별표 17** (자가품질검사 기록 보존 2~3년)
- **축산물 위생관리법** (해당 시)

### 6.2 외부 인증 대응
- HACCP (필수)
- ISO 22000 (Food Safety Management)
- BRC Food (수출용, 선택)

### 6.3 기록 보존 요구
| 기록 종류 | 보존 기간 | 형식 |
|----------|---------|------|
| HACCP 일지 | 3년 (자가품질) ~ 5년 (CCP) | 전자/종이 모두 가능 |
| LOT 추적 | 5년 이상 | 전자 권장 |
| X-Ray 이미지 | 권장 5년 | 전자 |
| 시정조치(CAPA) | 5년 | 전자 권장 |

---

## 7. 화면 목록

| 화면 ID | 화면명 | 사용자 | 우선순위 |
|---------|--------|--------|---------|
| SCR-Q-01 | 통합 품질 대시보드 | 품질팀장 | Must |
| SCR-FVAL-01 | F-value 실시간 차트 | 살균 담당자 | Must |
| SCR-FVAL-02 | F-value AI 예측 알림 | 살균 담당자 | Must |
| SCR-FVAL-03 | CCP 이탈 시정조치 워크플로우 | 품질팀 | Must |
| SCR-XRAY-01 | X-Ray 검사 모니터링 | X-Ray 담당자 | Must |
| SCR-XRAY-02 | 이물 분류 결과 + 이미지 뷰어 | X-Ray 담당자 | Must |
| SCR-XRAY-03 | 이물 통계 대시보드 | 품질팀장 | Must |
| SCR-HACCP-01 | HACCP 모바일 점검 앱 | HACCP 점검자 | Must |
| SCR-HACCP-02 | CCP IoT 모니터링 대시보드 | 품질팀 | Must |
| SCR-HACCP-03 | RAG 법규 검색 챗봇 | 품질팀장 | Must |
| SCR-HACCP-04 | HACCP 자동 리포트 생성 | 품질팀장 | Must |
| SCR-Q-MODEL-01 | AI 모델 정확도 모니터링 | 품질팀장, IT | Should |

---

## 8. 우선순위 매트릭스 (MoSCoW)

### Must Have (Phase 1, 2026 Q3-Q4)
- F-value 자동 계산, 실시간 차트, IoT 데이터 수집, AI 예측(LSTM)
- AutoEncoder 이상 감지, XGBoost CCP 분류, 자동 LOT 격리
- X-Ray LOT 연계, CNN 이물 분류, NG 자동 격리, 통계 대시보드
- HACCP 모바일 점검 앱, IoT CCP 모니터링
- RAG 법규 검색 AI Agent, HACCP 자동 리포트

### Should Have (Phase 2, 2027 Q1)
- 모델 정확도 모니터링/재학습, X-Ray 이미지 5년 보관
- 수동 재판정 학습 피드백 루프
- 시정조치(CAPA) 워크플로우, 법규 변경 모니터링

### Nice to Have (Phase 3, 2027 Q2 이후)
- 외부 감사(BRC/ISO22000) 자동 자료 패키징

---

## 9. 의존성 및 가정

### 의존성
- **LOT 트레이서빌리티 모듈** (PM1 Plan)
- **IoT 인프라**: 살균기/검사기 OPC-UA 연계 (인프라팀)
- **X-Ray 장비**: 두손푸드 기존 보유 모델 인터페이스 사양 확인 필요
- **AI 학습 데이터**: 최소 3개월간의 F-value/X-Ray 운영 데이터 필요
- **법규 RAG 데이터**: 식약처 고시·식품위생법 PDF/HTML 크롤링

### 가정
- 살균기 3대, X-Ray 2대 운영 가정
- HACCP CCP 7개 (살균, 금속검출, X-Ray, 입고검사, 보관온도, 출고검사, 위생)
- AI 학습용 GPU 인프라 (학습) + CPU 추론 가능한 경량 모델 (현장)

---

## 10. 리스크 및 대응

| 리스크 | 영향도 | 대응 |
|--------|--------|------|
| AI 모델 학습 데이터 부족 | High | 시뮬레이션 데이터 + Transfer Learning |
| X-Ray 장비 인터페이스 비표준 | High | Adapter 패턴 + 벤더 협업 |
| 식약처 점검 시 디지털 기록 인정 여부 | High | 식약처 사전 검토, 전자서명 적용 |
| AI 오판으로 인한 정상 LOT 격리 | Medium | Confidence Threshold + 사람 검수 |
| 살균 공정 정전 시 데이터 손실 | High | 엣지 디바이스 로컬 캐싱 + UPS |
| 법규 RAG의 환각(Hallucination) | Medium | 출처 강제 + 신뢰도 표시 + 면책 고지 |

---

## 11. 다음 단계

1. 본 Plan 문서 CTO 승인
2. Designer3 → 화면 설계 (UI3_quality_equipment_haccp_design.md)
3. Architect → AI/ML 파이프라인 설계 (ARCH_system_architecture.md)
4. PM1/PM3 Plan과 Cross-Reference 확인 (특히 LOT 연계, AI Agent 통합)

**승인 요청**: CTO Lead
