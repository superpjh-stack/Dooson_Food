# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Dooson-AI-MES** is a Manufacturing Execution System (MES) with AI capabilities for **두손푸드 (Dooson Food)**, a food manufacturing company. The system is planned as a smart factory platform focused on AI-native manufacturing workflows.

- Business proposal: `3. [사업계획서] 제조AI특화 스마트공장 사업계획서_두손푸드_20260423_v0.95.pdf`
- Development level: **Dynamic** (fullstack with backend/frontend)
- PDCA phase tracker: `docs/.pdca-status.json`

## Development Methodology

This project uses the **bkit AI-native development framework** with PDCA methodology:

- Phase 1: Schema & data model design (`/phase-1-schema`)
- Phase 2: Coding conventions (`/phase-2-convention`)
- Phase 3: UI mockups (`/phase-3-mockup`)
- Phase 4: API design & implementation (`/phase-4-api`)
- Phase 5: Design system (`/phase-5-design-system`)
- Phase 6: UI integration (`/phase-6-ui-integration`)
- Phase 7: SEO & security (`/phase-7-seo-security`)
- Phase 8: Gap analysis & review (`/phase-8-review`)
- Phase 9: Deployment (`/phase-9-deployment`)

Before implementing any feature: check/create Plan and Design documents in `docs/`. After implementation: run gap analysis with `bkit:gap-detector`.

## Project Status

Phase 1 Schema complete. Next: Phase 2 coding conventions.

## Domain Terminology

Always reference `docs/01-plan/glossary.md` when using business terms.
Key mappings: `Lot` (LOT/배치), `WorkOrder` (생산지시), `Ccp` (중요관리점), `FValue` (F값/살균효과지수), `LotLineage` (Closure Table for LOT traceability).

## Schema & Data Model

- Full SQL schema: `docs/01-plan/schema.md`
- Domain model & event flows: `docs/01-plan/domain-model.md`
- LOT traceability uses **Closure Table** pattern (`lot_lineage` table)
- Time-series tables (`iot_sensor_readings`, `f_value_temperature_series`) are **TimescaleDB hypertables**
- LOT code format: `DS-{YYYYMMDD}-{product_code}-{seq}` e.g. `DS-20261201-HMR001-0001`
- WorkOrder code format: `WO-{YYYYMMDD}-{4-digit-seq}` e.g. `WO-20261201-0001`

## Tech Stack

- **Frontend**: Next.js 14+ App Router, TypeScript, Tailwind CSS, shadcn/ui, Recharts, Socket.io, TanStack Query, Zustand
- **Backend**: Python 3.12 + FastAPI (async), SQLAlchemy 2.0, Alembic, Pydantic v2, Celery + Redis
- **Database**: PostgreSQL 16 + TimescaleDB, Redis 7, MinIO (files), Qdrant (RAG vectors)
- **AI/ML**: PyTorch (LSTM/AutoEncoder/CNN), XGBoost, LangGraph, LangChain, MLflow, Ray Serve
- **IoT**: OPC-UA, Modbus TCP, MQTT (Mosquitto), Node-RED
- **Infra**: Docker Compose (dev), K3s (prod), NGINX, GitHub Actions, Prometheus + Grafana
- **Package manager**: npm (frontend), pip/uv (backend)

## Coding Conventions

Full conventions: `CONVENTIONS.md`
- Naming details: `docs/01-plan/naming.md`
- Folder structure: `docs/01-plan/structure.md`
- Env vars template: `.env.example`

Key rules to remember:
- TS: single quotes, no semicolons, 2-space indent, no `any`
- Python: snake_case functions, PascalCase classes, 100 char line length (ruff/black)
- AI predictions: always show `confidence` score in UI — never display raw AI output without it
- LOT status changes: only via `LotService.hold()` — never direct DB update
- HACCP records: soft delete only (`deleted_at`), hard delete is forbidden
- DB mocks in tests: forbidden — use real test DB (docker compose)

## Key bkit Commands

```bash
# Start a new PDCA cycle for a feature
/pdca plan {feature-name}

# Run gap analysis after implementation
/pdca analyze {feature-name}

# CTO-led agent team orchestration
/pdca team {feature-name}
```

## MES Domain Context

Core domains: Production (생산) → LOT Traceability → Quality/HACCP → Equipment → AI Agent Hub → KPI Dashboard.

Critical domain rules:
- LOT `ON_HOLD` status is set automatically on CCP deviation or X-Ray NG
- BOM version is locked at WorkOrder creation time — mid-order BOM changes don't apply
- HACCP records require 2-year retention + electronic signature (식약처 규정)
- AI predictions always show `confidence` score and source reference in UI
