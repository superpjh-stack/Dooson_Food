# 두손푸드 AI-MES 목업 명세서

**버전**: v1.0 | **작성일**: 2026-05-04 | **단계**: Phase 3 Mockup

---

## 1. 디자인 토큰

| 토큰 | 값 | 용도 |
|------|-----|------|
| `--color-primary` | `#0F4C81` | 공업 블루 — 주요 UI, 버튼 |
| `--color-secondary` | `#1B5E20` | 두손푸드 그린 — 정상/합격 |
| `--color-accent` | `#00BCD4` | 청록 — AI 예측, 데이터 하이라이트 |
| `--color-critical` | `#D32F2F` | 긴급/이탈/NG |
| `--color-warning` | `#F57C00` | 경고/주의 |
| `--sidebar-bg` | `#0D1B2A` | 사이드바 다크 배경 |
| `--font-sans` | Pretendard / Noto Sans KR | 본문 |
| `--font-mono` | JetBrains Mono | LOT 코드, 수치 |

---

## 2. 화면 목록 및 Next.js 컴포넌트 매핑

### 2.1 메인 대시보드 (`pages/index.html`)

| 목업 영역 | Next.js 컴포넌트 | Props |
|----------|----------------|-------|
| KPI 카드 5개 | `components/kpi/KpiCard.tsx` | `label`, `value`, `unit`, `delta`, `color` |
| 생산지시 테이블 | `components/production/WorkOrderTable.tsx` | `workOrders: WorkOrder[]` |
| 설비 OEE 섹션 | `components/equipment/OeePanel.tsx` | `equipmentList: Equipment[]` |
| 알림센터 | `components/alerts/AlertCenter.tsx` | `alerts: Alert[]` |
| AI Agent 챗 | `components/ai/AgentChatPanel.tsx` | `domain: 'haccp'\|'production'\|...` |
| F-value 미니차트 | `components/charts/FValueMiniChart.tsx` | `records: FValuePoint[]`, `aiPrediction` |

### 2.2 LOT 추적 (`pages/lot-trace.html`)

| 목업 영역 | Next.js 컴포넌트 | Props |
|----------|----------------|-------|
| 검색바 | `components/lot/LotSearchBar.tsx` | `onSearch(code)`, `direction` |
| 회수 경보 배너 | `components/lot/RecallAlertBanner.tsx` | `affectedLots: Lot[]` |
| LOT 기본정보 카드 | `components/lot/LotInfoCard.tsx` | `lot: Lot` |
| 품질 이력 타임라인 | `components/lot/QualityTimeline.tsx` | `ccpRecords`, `xrayResult` |
| LOT 계보 트리 | `components/lot/LotTree.tsx` | `rootLot: Lot`, `lineage: LotLineageNode[]` |
| 회수 시뮬레이션 표 | `components/lot/RecallSimTable.tsx` | `affectedLots: Lot[]` |

### 2.3 품질 모니터링 (`pages/quality.html`)

| 목업 영역 | Next.js 컴포넌트 | Props |
|----------|----------------|-------|
| CCP 상태 그리드 | `components/quality/CcpStatusGrid.tsx` | `ccps: CcpStatus[]`, `line` |
| F-value 차트 | `components/charts/FValueChart.tsx` | `series: FValuePoint[]`, `aiPrediction`, `threshold` |
| CCP 기록 테이블 | `components/quality/CcpRecordTable.tsx` | `records: CcpRecord[]` |
| X-Ray 패널 | `components/quality/XRayPanel.tsx` | `stats: XRayStat`, `latestNg?: XRayResult` |
| Grad-CAM 이미지 | `components/quality/XRayGradCam.tsx` | `imageUrl`, `gradCamUrl`, `result` |
| HACCP AI 권고 | `components/ai/HaccpRecommendation.tsx` | `deviation: CcpRecord`, `recommendation` |

---

## 3. 공통 컴포넌트

| 컴포넌트 | 파일 | 설명 |
|---------|------|------|
| `LotStatusBadge` | `components/lot/LotStatusBadge.tsx` | ACTIVE/ON_HOLD/SHIPPED/RECALLED 배지 |
| `SeverityBadge` | `components/alerts/SeverityBadge.tsx` | CRITICAL/WARNING/INFO 배지 |
| `AiConfidenceBar` | `components/ai/AiConfidenceBar.tsx` | AI 신뢰도 + 출처 표시 (필수) |
| `ProgressBar` | `components/ui/ProgressBar.tsx` | 생산 진척률 바 |
| `StatusDot` | `components/ui/StatusDot.tsx` | 실시간 설비 상태 점 |
| `MiniBarChart` | `components/charts/MiniBarChart.tsx` | 소형 막대 차트 |

---

## 4. AI 표시 규칙 (UI 필수 준수)

```
confidence < 0.6  → 표시하지 않음
confidence 0.6~0.8 → 주의 표시 (노란색 바)
confidence >= 0.8  → 정상 표시 (청록색 바)

반드시 함께 표시:
- confidence 수치 (%)
- 모델명 또는 출처 문서명
- 예측 시각
```

---

## 5. 반응형 대응 계획

| 화면 | 목표 기기 | 레이아웃 변경 |
|------|---------|-------------|
| `index.html` | PC 1920px | 5열 KPI → 3열 |
| `lot-trace.html` | PC 1440px | 2열 → 1열 (태블릿) |
| `quality.html` | PC 1440px | 2열 → 1열 |
| 태블릿 현장앱 | iPad 1024px | 사이드바 숨김 + 하단 네비 |
| 모바일 점검앱 | Mobile 390px | 단열 + 터치 최적화 |

---

## 6. Phase 4 전환 체크리스트

- [x] 색상 토큰 → Tailwind CSS 커스텀 설정으로 전환
- [x] JSON 목업 데이터 → API 응답 스키마 확정 (`/api/v1/...`)
- [x] 컴포넌트 Props 인터페이스 → TypeScript 타입 정의
- [ ] shadcn/ui 컴포넌트로 기본 UI 교체 (Button, Card, Table, Badge)
- [ ] TanStack Query로 API 연동
- [ ] Socket.io로 실시간 CCP/센서 데이터 연동
