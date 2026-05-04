# Gap Analysis Report — `dooson-ai-mes`

**Latest Check**: Check-2 (after Act-1) | **Match Rate: 64%** | Target: 90%  
**Check-1 baseline**: 34% | **Delta**: +30pp  

**Project**: 두손푸드 AI-MES (Dooson Food AI Manufacturing Execution System)  
**Level**: Dynamic (fullstack)  
**PDCA Phase**: Check  
**Analyst**: bkit:gap-detector

---

## 1. Executive Summary

| Metric | Value |
|---|---|
| **Overall Match Rate** | **34%** |
| Backend Domain Coverage | 2 / 7 domains (29%) |
| Frontend Component Coverage | 11 / ~16 designed (~69%) |
| Page/Route Coverage | 0 / 8+ planned routes (0%) |
| Schema-to-Model Coverage | 6 / 22 tables (27%) |
| Convention Compliance | 90% |
| Design System Token Usage | 95% |

**Verdict**: The implementation is a **vertical slice prototype** that proves the most critical/risky patterns (Closure Table traceability + CCP→LotHold cascade + AI confidence rule), but is far from feature-complete. Match Rate < 70% requires a pdca-iterate cycle. The implemented slice is **high quality** — strong adherence to conventions, design tokens, and architectural rules. The gap is one of **breadth** (missing domains and pages), not **depth**.

---

## 2. Domain-by-Domain Breakdown

| Domain | Schema Tables | Backend | Frontend Components | Match Rate |
|---|---|---|---|---|
| 사용자/Auth | `users` | ❌ None | ❌ None | **0%** |
| 제품/BOM | `products`, `boms`, `bom_items` | ❌ None | ❌ None | **0%** |
| 생산 (Production) | `production_lines`, `processes`, `work_orders`, `process_records` | ❌ None | ❌ None | **0%** |
| LOT 트레이서빌리티 | `lots`, `lot_lineage` | ✅ Full (router+service+repo+models) | ✅ LotStatusBadge, LotTypeBadge, LotTree | **~85%** |
| 품질 (Quality) | `ccps`, `ccp_records`, `f_value_records`, `f_value_temperature_series`, `xray_results` | ⚠ Partial (CCP+F-value+X-Ray; timeseries hypertable missing) | ✅ CcpStatusCard, FValueChart | **~55%** |
| 설비 (Equipment) | `equipment`, `maintenance_records`, `iot_sensor_readings`, `equipment_oee_hourly` | ❌ None | ⚠ StatusDot primitive only | **~10%** |
| HACCP | `haccp_check_plans`, `haccp_check_records` | ❌ None | ❌ None | **0%** |
| 알림 (Notification) | `notifications` | ❌ None (print() placeholders) | ⚠ AlertItem UI only | **~15%** |
| AI Agent Hub | (LangGraph layer) | ❌ None | ❌ None | **0%** |
| KPI | (derived/aggregate) | ❌ None | ✅ KpiCard component | **~20%** |
| Layout/Shared | — | ✅ exception handler + base model + pagination | ✅ Sidebar, TopBar | **~85%** |

---

## 3. Prioritized Gap List

### 🔴 CRITICAL — Blocks core MES operation

| # | Gap | Design Reference | Impact |
|---|---|---|---|
| C1 | **Production domain entirely missing** — no `WorkOrder`, `ProcessRecord`, `ProductionLine`, `Process` models/endpoints | `schema.md` §4, mockup `index.html` (오늘의 생산지시) | LOT creation depends on `work_order_id` FK |
| C2 | **`work_orders` table referenced as FK but not modeled** — `Lot.work_order_id` and `CcpRecord.work_order_id` point to nowhere | `lot/models.py:20`, `quality/models.py:34` | DB migrations will fail FK integrity |
| C3 | **Auth/User domain missing** — no JWT, no `get_current_user`, no `User` model | `schema.md` §2, CLAUDE.md | All endpoints unauthenticated; 식약처 전자서명 impossible |
| C4 | **HACCP domain entirely missing** | `schema.md` §8 | Regulatory blocker: 2-year retention + 전자서명 법적 요건 |
| C5 | **Equipment domain missing on backend** — `sterilizer_id`/`machine_id` in quality models point to nothing | `schema.md` §7 | Predictive maintenance, OEE, F-value sterilizer linkage broken |
| C6 | **No frontend pages** — `apps/web/src/app/` has only `globals.css`; no `layout.tsx`, no routes | `structure.md` §2.1, mockup HTML files | UI components are unmounted — no running web app |
| C7 | **No API client / service layer / hooks on frontend** — no `lib/api/client.ts`, `services/*.ts`, `hooks/`, `stores/`, `types/` | `structure.md` §2.1, CONVENTIONS.md §3 | Frontend cannot call backend at all |
| C8 | **AI Agent Hub completely absent** | `structure.md` §3, mockup `index.html:310-336` | Core differentiator (제조AI특화) unbuilt |

### 🟠 MAJOR — Important features partially or not implemented

| # | Gap | Impact |
|---|---|---|
| M1 | TimescaleDB hypertables not modeled (`f_value_temperature_series`, `iot_sensor_readings`) | F-value chart cannot pull real time-series data |
| M2 | Notification domain only emits `print()` — no WebSocket layer | CCP/X-Ray alerts will not reach users |
| M3 | `list_lots`, `list_ccps`, `list_xray_results` endpoints return empty `[]` | API surface looks present but is non-functional |
| M4 | `get_lot` endpoint has broken DI — `repo = LotRepository(service.repo.db)` | Convention violation; silently breaks on rename |
| M5 | `f_value_records.is_passed` never set; `create_f_value_record()` doesn't compute `f0_calculated` | Auto-hold cascade for failed sterilization cannot fire |
| M6 | `CcpRecord.work_order_id nullable=False` but no FK target | Orphan FKs once `work_orders` table is added |
| M7 | Mockup screens not realized as Next.js pages | Stakeholder cannot see the system end-to-end |
| M8 | `POST /lots/recall-simulation` implemented but no UI | Designed recall simulation unreachable to users |
| M9 | Frontend utils/types directory structure missing vs. `structure.md` | Folder-structure convention violation |
| M10 | Pagination defined but never used in list endpoints | List endpoints won't scale |
| M11 | No tests at all; `pyproject.toml` has pytest deps but no test files | LOT lineage 5-second performance test (mandatory per CLAUDE.md) absent |
| M12 | No Alembic migrations — `alembic/` directory missing | DB schema cannot be applied to fresh instance |

### 🟡 MINOR — Small deviations

| # | Gap |
|---|---|
| m1 | `SoftDeleteMixin` defined but not applied to any model |
| m2 | `print()` used for logging instead of `logging` module (`logger.info()`) |
| m3 | AI confidence threshold `0.6` duplicated in frontend utils and backend config |
| m4 | **`LotStatusBadge.tsx` uses raw Tailwind colors (`bg-blue-50`, `bg-yellow-50`, `bg-green-50`)** — design-system rule "색상 직접 사용 금지" violated |
| m5 | Sidebar nav uses Unicode emoji instead of Lucide icons (tech stack specifies Lucide via shadcn/ui) |
| m6 | Dead import in `lot/models.py:9-10` (`TimestampMixin` and `Base` unused) |
| m7 | `lot/router.py:48` — imports inside function body (antipattern) |
| m8 | API path naming ambiguity: `naming.md` and `domain-model.md` differ on LOT path prefix |
| m9 | `config.py` uses `.env` while convention says `.env.local` |
| m10 | CORS hardcodes `localhost:3000-3002` instead of env-driven `CORS_ORIGINS` |

---

## 4. Convention Compliance Detail

| Convention Rule | Status | Evidence |
|---|---|---|
| TS: single quotes, no semicolons, 2-space indent | ✅ Pass | All .tsx files |
| TS: no `any` | ✅ Pass | No any found |
| Python: snake_case fn / PascalCase class / 100 char line | ✅ Pass | service.py files |
| AI confidence hide < 0.6 | ✅ Pass | `AiConfidenceBar.tsx:28` |
| LOT status only via `LotService.hold()` | ✅ Pass | `quality/service.py:69` — but `LotRepository.update_status()` is public (should be `_update_status`) |
| HACCP soft-delete only | ⏳ Not testable — domain not built |
| DB mocks forbidden | ⏳ N/A — no tests |
| Folder structure (services/, hooks/, types/, stores/) | ⚠ Partial | Frontend missing services/, hooks/, types/, lib/api/ |
| Backend router/service/repository layers | ✅ lot domain; ⚠ quality has no repository.py | |
| Color token usage (no raw Tailwind) | **⚠ VIOLATION** in `LotStatusBadge.tsx:26-28` | `bg-blue-50`, `bg-yellow-50`, `bg-green-50` |

---

## 5. Schema vs SQLAlchemy Coverage

| Schema Table | Model | Status |
|---|---|---|
| users | — | ❌ |
| products | — | ❌ |
| boms | — | ❌ |
| bom_items | — | ❌ |
| production_lines | — | ❌ |
| processes | — | ❌ |
| work_orders | — | ❌ **CRITICAL FK target** |
| process_records | — | ❌ |
| lots | `Lot` | ✅ |
| lot_lineage | `LotLineage` | ✅ |
| ccps | `Ccp` | ✅ |
| ccp_records | `CcpRecord` | ✅ |
| f_value_records | `FValueRecord` | ✅ |
| f_value_temperature_series | — | ❌ TimescaleDB hypertable |
| xray_results | `XRayResult` | ✅ |
| equipment | — | ❌ |
| maintenance_records | — | ❌ |
| iot_sensor_readings | — | ❌ TimescaleDB hypertable |
| equipment_oee_hourly | — | ❌ materialized view |
| haccp_check_plans | — | ❌ |
| haccp_check_records | — | ❌ |
| notifications | — | ❌ |

**Coverage: 6 / 22 = 27%**

---

## 6. Recommended Iteration Order (for `/pdca iterate`)

1. **Production domain** (C1, C2): WorkOrder model + CRUD endpoints — unlocks meaningful LOT creation
2. **Auth domain** (C3): User model + JWT + `get_current_user` dependency
3. **Alembic baseline migration** (M12): all 22 tables + `create_hypertable()` calls for TimescaleDB
4. **Equipment domain** (C5): models + router + MQTT subscriber stub
5. **HACCP domain** (C4): models + router + `SoftDeleteMixin` applied
6. **Frontend wiring** (C6, C7, M7):
   - `lib/api/client.ts` (axios + auth interceptor)
   - `services/lot.service.ts`, `services/quality.service.ts`
   - `hooks/use-lot-trace.ts`, `hooks/use-ccp-records.ts`
   - `app/layout.tsx`, `app/(dashboard)/layout.tsx`, dashboard page, LOT trace page, quality page
7. **Notification + WebSocket** (M2): Socket.io hub, replace `print()` placeholders
8. **TimescaleDB hypertables** (M1) + Celery F-value calculation task
9. **AI Agent Hub stub** (C8): one working `haccp_agent` with confidence score
10. **Convention fixes**: `LotStatusBadge` raw colors → semantic tokens; `print()` → `logger`; Lucide icons

**Target after iteration**: Match Rate ≥ 70%
