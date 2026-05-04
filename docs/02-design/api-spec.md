# 두손푸드 AI-MES API 명세서

**버전**: v1.0 | **작성일**: 2026-05-04 | **단계**: Phase 4 API
**Base URL**: `http://localhost:8000/api/v1`
**인증**: Bearer JWT (Access Token 1h, Refresh 7d)

---

## 공통 응답 형식

```json
// 단일 리소스
{ "data": { ... }, "meta": { "timestamp": "..." } }

// 목록
{ "data": [...], "pagination": { "page": 1, "limit": 20, "total": 100 } }

// 오류
{ "error": { "code": "CCP_DEVIATION", "message": "CCP 기준값 이탈", "details": [...] } }
```

---

## 1. 인증 (Auth)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/auth/login` | 로그인 → Access + Refresh Token |
| POST | `/auth/refresh` | Access Token 갱신 |
| POST | `/auth/logout` | 로그아웃 (Refresh Token 무효화) |
| GET  | `/auth/me` | 현재 사용자 정보 |

---

## 2. 생산관리 (Production)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET  | `/production/work-orders` | 목록 (status, date, line_id 필터) |
| POST | `/production/work-orders` | 생산지시 등록 |
| GET  | `/production/work-orders/{id}` | 상세 |
| PATCH| `/production/work-orders/{id}` | 상태 변경, 라인 배정 |
| POST | `/production/work-orders/{id}/release` | 지시 발행 (PLANNED→RELEASED) |
| GET  | `/production/process-records` | 공정 실적 목록 |
| POST | `/production/process-records` | 공정 실적 등록 |

---

## 3. LOT 트레이서빌리티 (Lot)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET  | `/lots` | 목록 (type, status, product_id 필터) |
| POST | `/lots` | LOT 생성 (Closure Table 자동 생성) |
| GET  | `/lots/{id}` | 상세 |
| PATCH| `/lots/{id}/hold` | 보류 처리 (ON_HOLD) |
| PATCH| `/lots/{id}/release` | 보류 해제 |
| GET  | `/lots/{id}/trace/backward` | **역추적**: 완제품→원자재 전체 계보 |
| GET  | `/lots/{id}/trace/forward` | **전방추적**: 원자재→영향 완제품 목록 |
| GET  | `/lots/{id}/trace/tree` | 계보 트리 (UI 렌더링용) |
| POST | `/lots/recall-simulation` | 회수 시뮬레이션 (원자재 LOT 기준) |
| GET  | `/lots/{id}/report` | LOT 이력 PDF 보고서 생성 |

**역추적 응답 예시**:
```json
{
  "data": {
    "target_lot": { "code": "DS-20261201-HMR001-0001", "type": "FG" },
    "ancestors": [
      { "lot": { "code": "DS-20261129-BEEF-018", "type": "RAW" }, "depth": 2 }
    ],
    "query_ms": 312
  }
}
```

---

## 4. 품질관리 (Quality)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET  | `/quality/ccps` | CCP 정의 목록 |
| GET  | `/quality/ccp-records` | CCP 모니터링 기록 (is_deviation 필터) |
| POST | `/quality/ccp-records` | CCP 측정값 기록 (이탈 시 자동 알림+LOT 보류) |
| PATCH| `/quality/ccp-records/{id}/corrective-action` | 시정조치 기록 |
| GET  | `/quality/f-value-records` | F-value 기록 목록 |
| POST | `/quality/f-value-records` | F-value 기록 생성 |
| GET  | `/quality/f-value-records/{id}/temperature-series` | 온도 시계열 (TimescaleDB) |
| POST | `/quality/f-value-records/{id}/temperature-series` | 온도 데이터 배치 수집 |
| GET  | `/quality/xray-results` | X-Ray 결과 목록 |
| POST | `/quality/xray-results` | X-Ray 판정 결과 등록 |

---

## 5. 설비관리 (Equipment)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET  | `/equipment` | 설비 목록 (line_id, status 필터) |
| GET  | `/equipment/{id}` | 설비 상세 + 현재 OEE |
| PATCH| `/equipment/{id}/status` | 설비 상태 변경 |
| GET  | `/equipment/{id}/sensors` | 최근 센서 데이터 (TimescaleDB) |
| GET  | `/equipment/{id}/oee` | OEE 집계 (hourly/daily/weekly) |
| GET  | `/equipment/maintenance-records` | 정비 기록 목록 |
| POST | `/equipment/maintenance-records` | 정비 요청 등록 |
| PATCH| `/equipment/maintenance-records/{id}` | 정비 상태 변경 |

---

## 6. HACCP

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET  | `/haccp/check-plans` | 점검 계획 목록 |
| GET  | `/haccp/check-records` | 점검 기록 목록 |
| POST | `/haccp/check-records` | 점검 기록 등록 |
| GET  | `/haccp/check-records/{id}` | 점검 기록 상세 |

---

## 7. 알림 (Notifications)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET  | `/notifications` | 내 알림 목록 (is_read 필터) |
| PATCH| `/notifications/{id}/read` | 읽음 처리 |
| PATCH| `/notifications/read-all` | 전체 읽음 |

---

## 8. WebSocket 이벤트

| 이벤트 | 방향 | 설명 |
|--------|------|------|
| `sensor:reading_updated` | Server→Client | IoT 센서 실시간 값 |
| `ccp:deviation_detected` | Server→Client | CCP 이탈 즉시 푸시 |
| `lot:status_changed` | Server→Client | LOT 상태 변경 |
| `equipment:fault_predicted` | Server→Client | AI 고장 예측 알림 |
| `notification:created` | Server→Client | 신규 알림 |

---

## 9. AI Agent (LangGraph)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/ai/chat` | AI Agent 대화 (domain 선택) |
| GET  | `/ai/predictions/f-value` | F-value AI 예측 |
| GET  | `/ai/predictions/equipment/{id}` | 설비 고장 예측 |

```json
// POST /ai/chat 요청
{ "message": "B라인 CCP 이탈 대응 방법 알려줘", "domain": "haccp", "context": { "lot_id": "..." } }
```
