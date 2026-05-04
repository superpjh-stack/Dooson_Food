# 두손푸드 AI-MES Design System

## Design Tokens

### Colors

| Token | HSL Value | Hex | Purpose |
|-------|-----------|-----|---------|
| `--primary` | 209 78% 28% | #0F4C81 | 공업 블루 — 주요 액션, 버튼 |
| `--secondary` | 123 55% 23% | #1B5E20 | 두손 그린 — 성공, 완료 상태 |
| `--accent` | 187 100% 42% | #00BCD4 | 청록 — AI/데이터 강조 |
| `--color-critical` | 0 70% 50% | #D32F2F | 부적합·CCP이탈·위험 |
| `--color-warning` | 30 100% 50% | #F57C00 | 경고·주의 |
| `--color-info` | 201 96% 43% | #0288D1 | 정보 |
| `--color-success` | 122 39% 49% | #388E3C | 정상·합격 |
| `sidebar` | 210 50% 10% | #0D1B2A | 사이드바 배경 |

### Typography

- **Heading**: `text-base font-semibold` (16px/600)
- **Body**: `text-sm` (14px/400)
- **Caption/Meta**: `text-xs` or `text-[11px]` (12px/10px)
- **Numeric data**: `tabular-nums` always applied to KPI/sensor values

### Spacing

Base: 4px grid. Key patterns:
- Card padding: `px-5 pt-5 pb-4`
- Section gap: `gap-4` (16px)
- Inline icon+text: `gap-2` (8px)

### Border Radius

- Cards: `rounded-lg` (8px)
- Badges: `rounded-full`
- Alert items: `rounded-sm` (2px) — industrial edge feel

---

## Component Catalog

### Primitives (apps/web/src/components/ui/)

| Component | File | Usage |
|-----------|------|-------|
| Badge | `badge.tsx` | Status labels — variants: success, critical, warning, info, muted, outline |
| Card | `card.tsx` | Content containers |
| StatusDot | `status-dot.tsx` | Equipment RUNNING/IDLE/FAULT/MAINTENANCE status |
| ProgressBar | `progress-bar.tsx` | Work order completion, OEE bars |

### AI Components (components/ai/)

| Component | Props | Rules |
|-----------|-------|-------|
| AiConfidenceBar | `confidence: number, modelName?, source?` | Hidden if confidence < 0.6 (CONVENTIONS) |

### LOT Components (components/lot/)

| Component | Usage |
|-----------|-------|
| LotStatusBadge | ACTIVE/ON_HOLD/CONSUMED/SHIPPED/RECALLED |
| LotTypeBadge | RAW(원자재)/WIP(반제품)/FG(완제품) |
| LotTree | Closure Table 기반 계보 트리 렌더링 |

### KPI Components (components/kpi/)

| Component | Usage |
|-----------|-------|
| KpiCard | 대시보드 상단 KPI 카드 (생산량, OEE, 품질률 등) |

### Alert Components (components/alerts/)

| Component | Usage |
|-----------|-------|
| AlertItem | CCP이탈, X-Ray NG, 설비 이상 알림 |

### Quality Components (components/quality/)

| Component | Usage |
|-----------|-------|
| CcpStatusCard | CCP 측정값 + 합격/불합격 + AI 신뢰도 |

### Chart Components (components/charts/)

| Component | Usage |
|-----------|-------|
| FValueChart | F값 시계열 — 실측(파란선) + AI예측(청록 점선) + 임계선(빨간 점선) |

### Layout Components (components/layout/)

| Component | Usage |
|-----------|-------|
| Sidebar | 좌측 고정 내비게이션 (다크 사이드바) |
| TopBar | 페이지 상단 제목 + 액션 영역 |

---

## Severity Rules (MES CONVENTIONS)

| Situation | Severity | Alert Variant | Badge Variant |
|-----------|----------|---------------|---------------|
| CCP 이탈 | CRITICAL | critical | critical |
| X-Ray NG | CRITICAL | critical | critical |
| LOT ON_HOLD | CRITICAL | critical | critical |
| F값 Warning 범위 | WARNING | warning | warning |
| AI 신뢰도 0.6~0.8 | — | — | (AiConfidenceBar: medium) |
| AI 신뢰도 < 0.6 | — | 표시 안 함 | — |
| 설비 FAULT | CRITICAL | critical | critical |
| 설비 MAINTENANCE | WARNING | warning | warning |

---

## Usage Patterns

### AI 신뢰도 표시 필수 조건

```tsx
// AI 예측 결과를 표시할 때는 반드시 AiConfidenceBar 함께 표시
<AiConfidenceBar confidence={0.87} modelName="LSTM-v2" />
// confidence < 0.6 이면 null 반환 (표시 안 함)
```

### LOT 상태 변경 금지

```tsx
// LOT 상태를 직접 변경하지 않음 — 반드시 API를 통해 LotService.hold() 호출
// ❌ lot.status = 'ON_HOLD'
// ✅ POST /api/v1/lots/{lot_id}/hold
```

### 색상 직접 사용 금지

```tsx
// ❌ className="text-red-500"
// ✅ className="text-critical"

// ❌ style={{ color: '#D32F2F' }}
// ✅ className="text-critical" (CSS variable 사용)
```
