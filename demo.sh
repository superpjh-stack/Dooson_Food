#!/usr/bin/env bash
# 두손푸드 AI-MES 데모 환경 실행 스크립트
set -e

COMPOSE_FILE="infra/docker/docker-compose.demo.yml"

case "${1:-up}" in
  up)
    echo "=================================================="
    echo " 두손푸드 AI-MES 데모 환경 시작"
    echo "=================================================="
    docker compose -f "$COMPOSE_FILE" up --build -d
    echo ""
    echo "⏳ 서비스 기동 대기 중..."
    sleep 5
    docker compose -f "$COMPOSE_FILE" logs migrate --no-log-prefix
    echo ""
    echo "=================================================="
    echo " ✅ 데모 환경 준비 완료"
    echo ""
    echo " 🌐 프론트엔드:  http://localhost:3000"
    echo " 🔌 API:          http://localhost:8000"
    echo " 📄 API 문서:    http://localhost:8000/docs"
    echo " 🔌 WebSocket:   ws://localhost:8000/ws/notifications"
    echo ""
    echo " 데모 계정:"
    echo "   admin   / admin1234!   (관리자)"
    echo "   op_kim  / op1234!      (생산 운영자)"
    echo "   qa_lee  / qa1234!      (품질 담당)"
    echo "   viewer  / view1234!    (조회 전용)"
    echo ""
    echo " 주요 시나리오:"
    echo "   LOT DS-20260503-HMR002-0002 → ON_HOLD"
    echo "   사유: CCP이탈(살균 117.3°C) + X-Ray NG(금속2.1mm) + F값 미달(7.82)"
    echo "=================================================="
    ;;
  down)
    echo "데모 환경 종료..."
    docker compose -f "$COMPOSE_FILE" down
    ;;
  reset)
    echo "데모 환경 초기화 (볼륨 포함)..."
    docker compose -f "$COMPOSE_FILE" down -v
    docker compose -f "$COMPOSE_FILE" up --build -d
    ;;
  logs)
    docker compose -f "$COMPOSE_FILE" logs -f "${2:-api}"
    ;;
  seed)
    echo "시드 데이터 재투입..."
    docker compose -f "$COMPOSE_FILE" exec api python -m seeds.seed_data
    ;;
  *)
    echo "사용법: ./demo.sh [up|down|reset|logs|seed]"
    ;;
esac
