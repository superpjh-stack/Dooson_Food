"""
두손푸드 AI-MES 데모 시드 데이터
HMR 레토르트 파우치 제조 시나리오 기반
실행: python -m seeds.seed_data
"""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

NOW = datetime.now(timezone.utc)
D = lambda days: NOW + timedelta(days=days)  # noqa: E731


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

async def exec(db: AsyncSession, sql: str, params: dict | None = None) -> None:
    await db.execute(text(sql), params or {})


async def insert_int(db: AsyncSession, table: str, sql: str, params: dict) -> int:
    """Execute a raw INSERT and return integer id."""
    result = await db.execute(text(sql), params)
    return result.scalar_one()


async def insert_uuid_row(db: AsyncSession, sql: str, params: dict) -> str:
    """Execute a raw INSERT and return UUID id as string."""
    result = await db.execute(text(sql), params)
    return str(result.scalar_one())


# ─────────────────────────────────────────────────────────────────────────────
# SEED FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

async def seed_users(db: AsyncSession) -> None:
    logger.info('[SEED] users...')
    rows = [
        ('admin', 'admin@dooson.co.kr', 'admin1234!', 'ADMIN', '시스템 관리자'),
        ('op_kim', 'kim@dooson.co.kr', 'op1234!', 'OPERATOR', '김철수'),
        ('qa_lee', 'lee@dooson.co.kr', 'qa1234!', 'QUALITY', '이영희'),
        ('viewer', 'viewer@dooson.co.kr', 'view1234!', 'VIEWER', '뷰어계정'),
    ]
    for username, email, password, role, full_name in rows:
        await exec(db,
            'INSERT INTO users (id,username,email,hashed_password,role,full_name,is_active,created_at)'
            ' VALUES (:id,:username,:email,:hashed_password,:role,:full_name,true,NOW())'
            ' ON CONFLICT (username) DO NOTHING',
            {
                'id': str(uuid.uuid4()),
                'username': username,
                'email': email,
                'hashed_password': pwd_context.hash(password),
                'role': role,
                'full_name': full_name,
            },
        )


async def seed_products(db: AsyncSession) -> dict[str, int]:
    logger.info('[SEED] products + BOMs...')
    products = [
        ('HMR001', '두손 갈비찜 HMR 500g', 'HMR', 'EA', 180),
        ('HMR002', '두손 된장찌개 레토르트 300g', 'HMR', 'EA', 365),
        ('HMR003', '두손 삼계탕 레토르트 800g', 'HMR', 'EA', 365),
        ('RAW001', '국내산 갈비육', '원자재', 'KG', 7),
        ('RAW002', '된장 (재래식)', '원자재', 'KG', 730),
        ('RAW003', '닭고기 (국내산 1+등급)', '원자재', 'KG', 5),
        ('PKG001', '레토르트 파우치 500ml', '포장재', 'EA', 1095),
    ]
    ids: dict[str, int] = {}
    for code, name, category, unit, shelf_life in products:
        pid = await insert_int(db,
            'products',
            'INSERT INTO products (code,name,category,unit,shelf_life_days,is_active,created_at)'
            ' VALUES (:code,:name,:category,:unit,:shelf_life_days,true,NOW()) RETURNING id',
            {'code': code, 'name': name, 'category': category, 'unit': unit, 'shelf_life_days': shelf_life},
        )
        ids[code] = pid

    # BOMs for HMR products
    bom_ids: dict[int, int] = {}
    bom_defs = [
        (ids['HMR001'], 'v1.2', D(-90), '갈비찜 표준 레시피 v1.2'),
        (ids['HMR002'], 'v2.0', D(-60), '된장찌개 레시피 개정'),
        (ids['HMR003'], 'v1.0', D(-30), '삼계탕 신규 레시피'),
    ]
    for product_id, version, effective_from, notes in bom_defs:
        bid = await insert_int(db,
            'boms',
            'INSERT INTO boms (product_id,version,is_active,effective_from,notes,created_at)'
            ' VALUES (:product_id,:version,true,:effective_from,:notes,NOW()) RETURNING id',
            {'product_id': product_id, 'version': version, 'effective_from': effective_from, 'notes': notes},
        )
        bom_ids[product_id] = bid

    # BOM items for HMR001
    bom_items = [
        (bom_ids[ids['HMR001']], 'RAW001', '국내산 갈비육', Decimal('0.3500'), 'KG', True),
        (bom_ids[ids['HMR001']], 'RAW002', '된장 (재래식)', Decimal('0.0200'), 'KG', False),
        (bom_ids[ids['HMR001']], 'PKG001', '레토르트 파우치 500ml', Decimal('1.0000'), 'EA', False),
    ]
    for bom_id, mat_code, mat_name, qty, unit, is_critical in bom_items:
        await exec(db,
            'INSERT INTO bom_items (bom_id,material_code,material_name,qty_per_unit,unit,is_critical,created_at)'
            ' VALUES (:bom_id,:material_code,:material_name,:qty_per_unit,:unit,:is_critical,NOW())',
            {'bom_id': bom_id, 'material_code': mat_code, 'material_name': mat_name,
             'qty_per_unit': qty, 'unit': unit, 'is_critical': is_critical},
        )
    return ids


async def seed_production_lines(db: AsyncSession) -> dict[str, int]:
    logger.info('[SEED] production_lines + processes...')
    lines = [
        ('LINE-A', 'A라인 (갈비찜/삼계탕)', Decimal('500'), 'EA'),
        ('LINE-B', 'B라인 (된장찌개/국물류)', Decimal('600'), 'EA'),
    ]
    line_ids: dict[str, int] = {}
    for code, name, capacity, unit in lines:
        lid = await insert_int(db,
            'production_lines',
            'INSERT INTO production_lines (code,name,capacity_per_hour,unit,is_active,created_at)'
            ' VALUES (:code,:name,:capacity_per_hour,:unit,true,NOW()) RETURNING id',
            {'code': code, 'name': name, 'capacity_per_hour': capacity, 'unit': unit},
        )
        line_ids[code] = lid

    # processes for LINE-A
    processes = [
        ('PROC-01', '원료 입고 및 검수', 1, line_ids['LINE-A'], 30, False),
        ('PROC-02', '세척 및 전처리', 2, line_ids['LINE-A'], 45, False),
        ('PROC-03', '조리 (배합/가열)', 3, line_ids['LINE-A'], 60, True),
        ('PROC-04', '충전 및 밀봉', 4, line_ids['LINE-A'], 30, False),
        ('PROC-05', '레토르트 살균 (CCP)', 5, line_ids['LINE-A'], 90, True),
        ('PROC-06', 'X-Ray 이물 검사 (CCP)', 6, line_ids['LINE-A'], 20, True),
        ('PROC-07', '냉각 및 포장', 7, line_ids['LINE-A'], 30, False),
        ('PROC-08', '출하 검사 및 입고', 8, line_ids['LINE-A'], 20, False),
    ]
    for code, name, seq, line_id, dur, is_ccp in processes:
        await exec(db,
            'INSERT INTO processes (code,name,sequence,line_id,standard_duration_minutes,is_ccp,created_at)'
            ' VALUES (:code,:name,:sequence,:line_id,:standard_duration_minutes,:is_ccp,NOW())',
            {'code': code, 'name': name, 'sequence': seq, 'line_id': line_id,
             'standard_duration_minutes': dur, 'is_ccp': is_ccp},
        )
    return line_ids


async def seed_equipment(db: AsyncSession) -> dict[str, str]:
    logger.info('[SEED] equipment...')
    equipment = [
        ('EQP-STR-01', '레토르트 살균기 #1', 'STERILIZER', 'RUNNING', Decimal('87.5'), D(-14)),
        ('EQP-STR-02', '레토르트 살균기 #2', 'STERILIZER', 'IDLE', Decimal('91.2'), D(-7)),
        ('EQP-XRY-01', 'X-Ray 이물 검출기 #1', 'XRAY', 'RUNNING', Decimal('95.0'), D(-3)),
        ('EQP-MIX-01', '배합기 (조리용) #1', 'MIXER', 'RUNNING', Decimal('82.3'), D(-21)),
        ('EQP-FIL-01', '충전기 (파우치) #1', 'FILLER', 'MAINTENANCE', Decimal('76.4'), D(0)),
        ('EQP-SEA-01', '밀봉기 #1', 'SEALER', 'RUNNING', Decimal('89.1'), D(-10)),
    ]
    eids: dict[str, str] = {}
    for code, name, etype, status, oee, last_maintained in equipment:
        eid = str(uuid.uuid4())
        await exec(db,
            'INSERT INTO equipment (id,code,name,type,status,oee,last_maintained_at,created_at)'
            ' VALUES (:id,:code,:name,:type,:status,:oee,:last_maintained_at,NOW())',
            {'id': eid, 'code': code, 'name': name, 'type': etype, 'status': status,
             'oee': oee, 'last_maintained_at': last_maintained},
        )
        eids[code] = eid
    return eids


async def seed_ccps(db: AsyncSession) -> dict[str, str]:
    logger.info('[SEED] CCPs...')
    # Migration: id, code, name, process_id, parameter, unit, limit_min, limit_max, monitoring_freq, is_active
    ccps = [
        ('CCP-01', '레토르트 살균 온도', '살균 중심 온도', '°C', Decimal('119.0'), Decimal('125.0'), 'PER_LOT'),
        ('CCP-02', '레토르트 살균 시간 (F값)', 'F0 값 달성 확인', 'min', Decimal('10.0'), None, 'PER_LOT'),
        ('CCP-03', 'X-Ray 이물 검출 감도', '금속/유리 검출 감도', 'mm', None, Decimal('1.5'), 'HOURLY'),
        ('CCP-04', '조리 중심 온도', '조리 중심 온도', '°C', Decimal('75.0'), None, 'PER_LOT'),
    ]
    ccp_ids: dict[str, str] = {}
    for code, name, parameter, unit, limit_min, limit_max, monitoring_freq in ccps:
        cid = str(uuid.uuid4())
        await exec(db,
            'INSERT INTO ccps (id,code,name,parameter,unit,limit_min,limit_max,monitoring_freq,is_active,created_at)'
            ' VALUES (:id,:code,:name,:parameter,:unit,:limit_min,:limit_max,:monitoring_freq,true,NOW())'
            ' ON CONFLICT (id) DO NOTHING',
            {'id': cid, 'code': code, 'name': name, 'parameter': parameter, 'unit': unit,
             'limit_min': limit_min, 'limit_max': limit_max, 'monitoring_freq': monitoring_freq},
        )
        ccp_ids[code] = cid
    return ccp_ids


async def seed_work_orders(
    db: AsyncSession, product_ids: dict[str, int], line_ids: dict[str, int]
) -> list[str]:
    logger.info('[SEED] work_orders...')
    # work_orders.id is UUID (no server_default) — must supply explicitly
    wos = [
        {
            'id': str(uuid.uuid4()),
            'code': 'WO-20260504-0001', 'product_id': product_ids['HMR001'],
            'production_line_id': line_ids['LINE-A'], 'planned_qty': Decimal('2000'),
            'actual_qty': Decimal('1950'), 'unit': 'EA', 'status': 'COMPLETED',
            'planned_start': D(-2), 'planned_end': D(-1),
            'actual_start': D(-2), 'actual_end': D(-1), 'bom_version': 'v1.2',
            'notes': '두손 갈비찜 정기 생산',
        },
        {
            'id': str(uuid.uuid4()),
            'code': 'WO-20260504-0002', 'product_id': product_ids['HMR002'],
            'production_line_id': line_ids['LINE-B'], 'planned_qty': Decimal('3000'),
            'actual_qty': Decimal('2850'), 'unit': 'EA', 'status': 'COMPLETED',
            'planned_start': D(-1), 'planned_end': D(0),
            'actual_start': D(-1), 'actual_end': D(0), 'bom_version': 'v2.0',
            'notes': '된장찌개 레토르트 정기 생산',
        },
        {
            'id': str(uuid.uuid4()),
            'code': 'WO-20260504-0003', 'product_id': product_ids['HMR001'],
            'production_line_id': line_ids['LINE-A'], 'planned_qty': Decimal('1500'),
            'actual_qty': Decimal('0'), 'unit': 'EA', 'status': 'IN_PROGRESS',
            'planned_start': D(0), 'planned_end': D(1),
            'actual_start': D(0), 'actual_end': None, 'bom_version': 'v1.2',
            'notes': '금일 생산 (진행중)',
        },
        {
            'id': str(uuid.uuid4()),
            'code': 'WO-20260504-0004', 'product_id': product_ids['HMR003'],
            'production_line_id': line_ids['LINE-A'], 'planned_qty': Decimal('1000'),
            'actual_qty': Decimal('0'), 'unit': 'EA', 'status': 'PLANNED',
            'planned_start': D(1), 'planned_end': D(2),
            'actual_start': None, 'actual_end': None, 'bom_version': 'v1.0',
            'notes': '삼계탕 생산 예정',
        },
    ]
    wo_ids: list[str] = []
    for wo in wos:
        await exec(db,
            'INSERT INTO work_orders (id,code,product_id,production_line_id,planned_qty,actual_qty,'
            'unit,status,planned_start,planned_end,actual_start,actual_end,bom_version,notes,created_at)'
            ' VALUES (:id,:code,:product_id,:production_line_id,:planned_qty,:actual_qty,'
            ':unit,:status,:planned_start,:planned_end,:actual_start,:actual_end,:bom_version,:notes,NOW())',
            wo,
        )
        wo_ids.append(wo['id'])
    return wo_ids


async def seed_lots(
    db: AsyncSession, wo_ids: list[str], product_ids: dict[str, int]
) -> dict[str, str]:
    """Create LOTs with Closure Table lineage: RAW → WIP → FG.
    lots.id = UUID, lots.product_id = INTEGER, lots.work_order_id = UUID.
    """
    logger.info('[SEED] lots + lot_lineage (Closure Table)...')

    def lot_row(code, lot_type, product_code, wo_idx, qty, unit, status='ACTIVE',
                received_at=None, produced_at=None, expiry_date=None) -> dict:
        return {
            'id': str(uuid.uuid4()),
            'code': code,
            'type': lot_type,
            'product_id': product_ids[product_code],  # INTEGER
            'work_order_id': wo_ids[wo_idx],           # UUID string
            'qty': Decimal(str(qty)),
            'unit': unit,
            'status': status,
            'received_at': received_at,
            'produced_at': produced_at,
            'expiry_date': expiry_date,
        }

    lots = [
        # WO-0001 완료 LOTs
        lot_row('DS-20260502-RAW001-0001', 'RAW', 'RAW001', 0, 700, 'KG',
                received_at=D(-3), expiry_date=D(4).date()),
        lot_row('DS-20260502-RAW002-0001', 'RAW', 'RAW002', 0, 40, 'KG',
                received_at=D(-3), expiry_date=D(727).date()),
        lot_row('DS-20260503-WIP001-0001', 'WIP', 'HMR001', 0, 1950, 'EA',
                produced_at=D(-2)),
        lot_row('DS-20260503-HMR001-0001', 'FG', 'HMR001', 0, 1950, 'EA',
                produced_at=D(-1), expiry_date=D(179).date()),
        # WO-0002 완료 — CCP 이탈로 일부 ON_HOLD
        lot_row('DS-20260503-RAW001-0002', 'RAW', 'RAW001', 1, 900, 'KG',
                received_at=D(-2), expiry_date=D(5).date()),
        lot_row('DS-20260503-WIP002-0001', 'WIP', 'HMR002', 1, 2850, 'EA',
                produced_at=D(-1)),
        lot_row('DS-20260503-HMR002-0001', 'FG', 'HMR002', 1, 2700, 'EA',
                produced_at=D(0), expiry_date=D(365).date()),
        lot_row('DS-20260503-HMR002-0002', 'FG', 'HMR002', 1, 150, 'EA',
                status='ON_HOLD', produced_at=D(0)),  # 핵심 데모 시나리오
        # WO-0003 진행중 LOTs
        lot_row('DS-20260504-RAW001-0003', 'RAW', 'RAW001', 2, 525, 'KG',
                received_at=D(0), expiry_date=D(7).date()),
        lot_row('DS-20260504-WIP003-0001', 'WIP', 'HMR001', 2, 1000, 'EA',
                produced_at=D(0)),
    ]

    lot_ids: dict[str, str] = {}
    for lot in lots:
        await exec(db,
            'INSERT INTO lots (id,code,type,product_id,work_order_id,qty,unit,status,'
            'received_at,produced_at,expiry_date,created_at)'
            ' VALUES (:id,:code,:type,:product_id,:work_order_id::uuid,:qty,:unit,:status,'
            ':received_at,:produced_at,:expiry_date,NOW())',
            lot,
        )
        lot_ids[lot['code']] = lot['id']

    # Closure Table
    lineage_pairs = [
        ('DS-20260502-RAW001-0001', 'DS-20260503-WIP001-0001', 1, 'INPUT', Decimal('350')),
        ('DS-20260502-RAW002-0001', 'DS-20260503-WIP001-0001', 1, 'INPUT', Decimal('39')),
        ('DS-20260503-WIP001-0001', 'DS-20260503-HMR001-0001', 1, 'PROCESSED', Decimal('1950')),
        ('DS-20260502-RAW001-0001', 'DS-20260503-HMR001-0001', 2, 'INPUT', Decimal('350')),
        ('DS-20260502-RAW002-0001', 'DS-20260503-HMR001-0001', 2, 'INPUT', Decimal('39')),
        ('DS-20260503-RAW001-0002', 'DS-20260503-WIP002-0001', 1, 'INPUT', Decimal('900')),
        ('DS-20260503-WIP002-0001', 'DS-20260503-HMR002-0001', 1, 'PROCESSED', Decimal('2700')),
        ('DS-20260503-WIP002-0001', 'DS-20260503-HMR002-0002', 1, 'PROCESSED', Decimal('150')),
        ('DS-20260503-RAW001-0002', 'DS-20260503-HMR002-0001', 2, 'INPUT', Decimal('900')),
        ('DS-20260503-RAW001-0002', 'DS-20260503-HMR002-0002', 2, 'INPUT', Decimal('50')),
        ('DS-20260504-RAW001-0003', 'DS-20260504-WIP003-0001', 1, 'INPUT', Decimal('350')),
        # Self-references (depth=0)
        *[(c, c, 0, 'SELF', None) for c in lot_ids.keys()],
    ]

    for anc, desc, depth, rtype, qty in lineage_pairs:
        if anc not in lot_ids or desc not in lot_ids:
            continue
        await exec(db,
            'INSERT INTO lot_lineage (ancestor_lot_id,descendant_lot_id,depth,relation_type,qty_used,created_at)'
            ' VALUES (:anc::uuid,:desc::uuid,:depth,:rtype,:qty,NOW())'
            ' ON CONFLICT DO NOTHING',
            {'anc': lot_ids[anc], 'desc': lot_ids[desc], 'depth': depth, 'rtype': rtype, 'qty': qty},
        )

    return lot_ids


async def seed_ccp_records(
    db: AsyncSession, ccp_ids: dict[str, str], wo_ids: list[str], lot_ids: dict[str, str]
) -> None:
    logger.info('[SEED] ccp_records...')
    # Migration columns: id, ccp_id, work_order_id, lot_id, measured_at, measured_value,
    #   measured_by (UUID nullable), is_deviation, corrective_action, photo_urls, verified_by, verified_at
    records = [
        # WO-0001 PASS
        {
            'id': str(uuid.uuid4()), 'ccp_id': ccp_ids['CCP-01'], 'work_order_id': wo_ids[0],
            'lot_id': lot_ids['DS-20260503-WIP001-0001'],
            'measured_at': D(-2) + timedelta(hours=3),
            'measured_value': Decimal('121.8'), 'measured_by': None, 'is_deviation': False,
        },
        {
            'id': str(uuid.uuid4()), 'ccp_id': ccp_ids['CCP-04'], 'work_order_id': wo_ids[0],
            'lot_id': lot_ids['DS-20260503-WIP001-0001'],
            'measured_at': D(-2) + timedelta(hours=2),
            'measured_value': Decimal('76.5'), 'measured_by': None, 'is_deviation': False,
        },
        # WO-0002 CCP 이탈 (핵심 시나리오)
        {
            'id': str(uuid.uuid4()), 'ccp_id': ccp_ids['CCP-01'], 'work_order_id': wo_ids[1],
            'lot_id': lot_ids['DS-20260503-HMR002-0002'],
            'measured_at': D(-1) + timedelta(hours=4),
            'measured_value': Decimal('117.3'), 'measured_by': None, 'is_deviation': True,
        },
        {
            'id': str(uuid.uuid4()), 'ccp_id': ccp_ids['CCP-01'], 'work_order_id': wo_ids[1],
            'lot_id': lot_ids['DS-20260503-HMR002-0001'],
            'measured_at': D(-1) + timedelta(hours=2),
            'measured_value': Decimal('122.1'), 'measured_by': None, 'is_deviation': False,
        },
        # WO-0003 진행중
        {
            'id': str(uuid.uuid4()), 'ccp_id': ccp_ids['CCP-04'], 'work_order_id': wo_ids[2],
            'lot_id': lot_ids['DS-20260504-WIP003-0001'],
            'measured_at': D(0) + timedelta(hours=1),
            'measured_value': Decimal('78.2'), 'measured_by': None, 'is_deviation': False,
        },
    ]
    for rec in records:
        await exec(db,
            'INSERT INTO ccp_records (id,ccp_id,work_order_id,lot_id,measured_at,'
            'measured_value,measured_by,is_deviation,created_at)'
            ' VALUES (:id,:ccp_id::uuid,:work_order_id::uuid,:lot_id::uuid,:measured_at,'
            ':measured_value,:measured_by::uuid,:is_deviation,NOW())',
            rec,
        )


async def seed_f_value_records(
    db: AsyncSession, wo_ids: list[str], lot_ids: dict[str, str], eids: dict[str, str]
) -> None:
    logger.info('[SEED] f_value_records...')
    # Migration columns: id, sterilizer_id, work_order_id, lot_id, start_time, end_time,
    #   f0_target, f0_calculated, is_passed, ai_prediction, ai_confidence
    fvrs = [
        {
            'id': str(uuid.uuid4()), 'sterilizer_id': eids['EQP-STR-01'],
            'work_order_id': wo_ids[0], 'lot_id': lot_ids['DS-20260503-WIP001-0001'],
            'start_time': D(-2) + timedelta(hours=3),
            'end_time': D(-2) + timedelta(hours=4, minutes=30),
            'f0_target': Decimal('10.00'), 'f0_calculated': Decimal('12.35'),
            'is_passed': True, 'ai_confidence': Decimal('0.9400'),
        },
        {
            'id': str(uuid.uuid4()), 'sterilizer_id': eids['EQP-STR-01'],
            'work_order_id': wo_ids[1], 'lot_id': lot_ids['DS-20260503-HMR002-0001'],
            'start_time': D(-1) + timedelta(hours=2),
            'end_time': D(-1) + timedelta(hours=3, minutes=40),
            'f0_target': Decimal('10.00'), 'f0_calculated': Decimal('11.87'),
            'is_passed': True, 'ai_confidence': Decimal('0.9100'),
        },
        # ON_HOLD LOT — F값 미달
        {
            'id': str(uuid.uuid4()), 'sterilizer_id': eids['EQP-STR-01'],
            'work_order_id': wo_ids[1], 'lot_id': lot_ids['DS-20260503-HMR002-0002'],
            'start_time': D(-1) + timedelta(hours=4),
            'end_time': D(-1) + timedelta(hours=5, minutes=10),
            'f0_target': Decimal('10.00'), 'f0_calculated': Decimal('7.82'),  # 미달
            'is_passed': False, 'ai_confidence': Decimal('0.9700'),
        },
    ]
    for fvr in fvrs:
        await exec(db,
            'INSERT INTO f_value_records (id,sterilizer_id,work_order_id,lot_id,'
            'start_time,end_time,f0_target,f0_calculated,is_passed,ai_confidence,created_at)'
            ' VALUES (:id,:sterilizer_id::uuid,:work_order_id::uuid,:lot_id::uuid,'
            ':start_time,:end_time,:f0_target,:f0_calculated,:is_passed,:ai_confidence,NOW())',
            fvr,
        )


async def seed_xray_results(
    db: AsyncSession, wo_ids: list[str], lot_ids: dict[str, str], eids: dict[str, str]
) -> None:
    logger.info('[SEED] xray_results...')
    # Migration columns: id, machine_id, work_order_id, lot_id, inspected_at, result,
    #   contaminant_type, contaminant_size, confidence, image_url, grad_cam_url,
    #   ai_classification, reviewed_by (UUID nullable)
    xrays = [
        {
            'id': str(uuid.uuid4()), 'machine_id': eids['EQP-XRY-01'],
            'work_order_id': wo_ids[0], 'lot_id': lot_ids['DS-20260503-WIP001-0001'],
            'inspected_at': D(-1) + timedelta(hours=5),
            'result': 'OK', 'contaminant_type': None, 'contaminant_size': None,
            'confidence': Decimal('0.9987'), 'image_url': '/xray/WO-0001-001.jpg',
            'reviewed_by': None,
        },
        {
            'id': str(uuid.uuid4()), 'machine_id': eids['EQP-XRY-01'],
            'work_order_id': wo_ids[1], 'lot_id': lot_ids['DS-20260503-WIP002-0001'],
            'inspected_at': D(0) + timedelta(hours=1),
            'result': 'OK', 'contaminant_type': None, 'contaminant_size': None,
            'confidence': Decimal('0.9954'), 'image_url': '/xray/WO-0002-001.jpg',
            'reviewed_by': None,
        },
        # NG — 이물 검출 (핵심 시나리오)
        {
            'id': str(uuid.uuid4()), 'machine_id': eids['EQP-XRY-01'],
            'work_order_id': wo_ids[1], 'lot_id': lot_ids['DS-20260503-HMR002-0002'],
            'inspected_at': D(0) + timedelta(hours=2),
            'result': 'NG', 'contaminant_type': 'METAL_FRAGMENT',
            'contaminant_size': Decimal('2.10'),
            'confidence': Decimal('0.9821'), 'image_url': '/xray/WO-0002-NG-001.jpg',
            'reviewed_by': None,
        },
    ]
    for xr in xrays:
        await exec(db,
            'INSERT INTO xray_results (id,machine_id,work_order_id,lot_id,'
            'inspected_at,result,contaminant_type,contaminant_size,'
            'confidence,image_url,reviewed_by,created_at)'
            ' VALUES (:id,:machine_id::uuid,:work_order_id::uuid,:lot_id::uuid,'
            ':inspected_at,:result,:contaminant_type,:contaminant_size,'
            ':confidence,:image_url,:reviewed_by::uuid,NOW())',
            xr,
        )


async def seed_haccp(
    db: AsyncSession, ccp_ids: dict[str, str], wo_ids: list[str], lot_ids: dict[str, str]
) -> None:
    logger.info('[SEED] haccp_check_plans + records...')
    # haccp_check_plans.id is UUID (no server_default) — supply explicitly
    plans = [
        {
            'id': str(uuid.uuid4()),
            'ccp_id': ccp_ids['CCP-01'],
            'check_frequency': 'PER_LOT',
            'check_method': '살균기 온도계 직독 및 데이터로거 기록',
            'corrective_action': '살균 재진행 또는 LOT 보류 후 책임자 보고',
            'responsible_person': 'qa_lee',
        },
        {
            'id': str(uuid.uuid4()),
            'ccp_id': ccp_ids['CCP-03'],
            'check_frequency': 'HOURLY',
            'check_method': 'X-Ray 검출기 감도 시험편 통과 확인',
            'corrective_action': '검출기 재조정 및 직전 1시간 생산분 전수검사',
            'responsible_person': 'op_kim',
        },
    ]
    plan_ids: list[str] = []
    for plan in plans:
        await exec(db,
            'INSERT INTO haccp_check_plans (id,ccp_id,check_frequency,check_method,'
            'corrective_action,responsible_person,is_active,created_at)'
            ' VALUES (:id,:ccp_id::uuid,:check_frequency,:check_method,'
            ':corrective_action,:responsible_person,true,NOW())',
            plan,
        )
        plan_ids.append(plan['id'])

    # haccp_check_records.id is UUID
    records = [
        {
            'id': str(uuid.uuid4()),
            'plan_id': plan_ids[0], 'lot_id': lot_ids['DS-20260503-WIP001-0001'],
            'work_order_id': wo_ids[0], 'checked_by': 'qa_lee',
            'checked_at': D(-2) + timedelta(hours=3, minutes=30),
            'result': 'PASS',
            'measured_values': '{"temperature": 121.8, "duration_min": 90}',
            'corrective_action_taken': None, 'deleted_at': None,
        },
        {
            'id': str(uuid.uuid4()),
            'plan_id': plan_ids[0], 'lot_id': lot_ids['DS-20260503-HMR002-0002'],
            'work_order_id': wo_ids[1], 'checked_by': 'qa_lee',
            'checked_at': D(-1) + timedelta(hours=4, minutes=15),
            'result': 'FAIL',
            'measured_values': '{"temperature": 117.3, "duration_min": 90}',
            'corrective_action_taken': 'LOT DS-20260503-HMR002-0002 보류 처리. 살균기 점검 및 재조정 완료.',
            'deleted_at': None,
        },
        {
            'id': str(uuid.uuid4()),
            'plan_id': plan_ids[1], 'lot_id': lot_ids['DS-20260503-WIP002-0001'],
            'work_order_id': wo_ids[1], 'checked_by': 'op_kim',
            'checked_at': D(-1) + timedelta(hours=1),
            'result': 'PASS',
            'measured_values': '{"test_piece": "1.5mm_metal", "detected": true}',
            'corrective_action_taken': None, 'deleted_at': None,
        },
    ]
    for rec in records:
        await exec(db,
            'INSERT INTO haccp_check_records (id,plan_id,lot_id,work_order_id,checked_by,'
            'checked_at,result,measured_values,corrective_action_taken,deleted_at,created_at)'
            ' VALUES (:id,:plan_id::uuid,:lot_id::uuid,:work_order_id::uuid,:checked_by,'
            ':checked_at,:result,:measured_values::jsonb,:corrective_action_taken,:deleted_at,NOW())',
            rec,
        )


async def seed_iot_sensor_readings(db: AsyncSession, eids: dict[str, str]) -> None:
    logger.info('[SEED] iot_sensor_readings (살균 온도 프로파일)...')
    sterilizer_id = eids['EQP-STR-01']
    sterilization_temps = [
        25.0, 45.2, 68.4, 89.1, 105.3, 115.7,
        120.2, 121.5, 121.8, 122.1, 122.0, 121.9,
        121.7, 121.8, 122.0, 121.5, 85.3, 45.2, 25.0,
    ]
    for i, temp in enumerate(sterilization_temps):
        await exec(db,
            'INSERT INTO iot_sensor_readings (equipment_id,sensor_type,value,unit,recorded_at,quality,created_at)'
            ' VALUES (:equip_id::uuid,:sensor_type,:value,:unit,:recorded_at,:quality,NOW())',
            {'equip_id': sterilizer_id, 'sensor_type': 'TEMPERATURE',
             'value': Decimal(str(temp)), 'unit': '°C',
             'recorded_at': D(0) - timedelta(minutes=38 - i * 2), 'quality': 'GOOD'},
        )
    for i in range(10):
        await exec(db,
            'INSERT INTO iot_sensor_readings (equipment_id,sensor_type,value,unit,recorded_at,quality,created_at)'
            ' VALUES (:equip_id::uuid,:sensor_type,:value,:unit,:recorded_at,:quality,NOW())',
            {'equip_id': sterilizer_id, 'sensor_type': 'PRESSURE',
             'value': Decimal(str(round(2.1 + i * 0.03, 2))), 'unit': 'bar',
             'recorded_at': D(0) - timedelta(minutes=20 - i * 2), 'quality': 'GOOD'},
        )


async def seed_notifications(
    db: AsyncSession, lot_ids: dict[str, str], wo_ids: list[str]
) -> None:
    logger.info('[SEED] notifications...')
    # notifications.id is UUID — supply explicitly
    notifs = [
        {
            'id': str(uuid.uuid4()),
            'type': 'CCP_DEVIATION', 'severity': 'CRITICAL',
            'title': 'CCP-01 이탈 감지: 살균 온도 미달',
            'body': 'LOT DS-20260503-HMR002-0002 살균 온도 117.3°C (기준: 119°C 이상). LOT 자동 보류 처리됨.',
            'lot_id': lot_ids['DS-20260503-HMR002-0002'],
            'work_order_id': wo_ids[1], 'is_read': False,
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'XRAY_NG', 'severity': 'CRITICAL',
            'title': 'X-Ray NG: 금속 이물 검출',
            'body': 'LOT DS-20260503-HMR002-0002에서 금속 파편 2.1mm 검출. AI 신뢰도 98.2%.',
            'lot_id': lot_ids['DS-20260503-HMR002-0002'],
            'work_order_id': wo_ids[1], 'is_read': False,
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'FVALUE_FAIL', 'severity': 'CRITICAL',
            'title': 'F값 목표 미달 (F0=7.82, 목표≥10)',
            'body': 'LOT DS-20260503-HMR002-0002 살균 효과 불충분. 재살균 또는 폐기 검토 필요.',
            'lot_id': lot_ids['DS-20260503-HMR002-0002'],
            'work_order_id': wo_ids[1], 'is_read': True,
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'EQUIPMENT_FAULT', 'severity': 'WARNING',
            'title': '설비 점검 중: 충전기 #1',
            'body': 'EQP-FIL-01 (충전기 #1) 정기 점검 중. 예상 복구: 금일 오후 3시.',
            'lot_id': None, 'work_order_id': None, 'is_read': False,
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'LOT_HOLD', 'severity': 'CRITICAL',
            'title': 'LOT 보류 처리: DS-20260503-HMR002-0002',
            'body': '사유: CCP_DEVIATION — 살균 온도 이탈. 담당자 확인 필요.',
            'lot_id': lot_ids['DS-20260503-HMR002-0002'],
            'work_order_id': wo_ids[1], 'is_read': True,
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'SYSTEM', 'severity': 'INFO',
            'title': 'WO-20260504-0001 생산 완료',
            'body': '두손 갈비찜 HMR 1,950EA 생산 완료. 목표 대비 달성률 97.5%.',
            'lot_id': None, 'work_order_id': wo_ids[0], 'is_read': True,
        },
    ]
    for n in notifs:
        await exec(db,
            'INSERT INTO notifications (id,type,severity,title,body,lot_id,work_order_id,is_read,created_at)'
            ' VALUES (:id,:type,:severity,:title,:body,:lot_id::uuid,:work_order_id::uuid,:is_read,NOW())',
            n,
        )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

async def run_seeds() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger.info('=' * 60)
    logger.info('두손푸드 AI-MES 시드 데이터 투입 시작')
    logger.info('=' * 60)

    async with AsyncSessionLocal() as db:
        try:
            logger.info('[SEED] 기존 데이터 초기화...')
            for tbl in [
                'notifications', 'haccp_check_records', 'haccp_check_plans',
                'xray_results', 'f_value_temperature_series', 'f_value_records',
                'ccp_records', 'lot_lineage', 'lots', 'process_records',
                'iot_sensor_readings', 'equipment', 'ccps', 'work_orders',
                'processes', 'production_lines', 'bom_items', 'boms',
                'products', 'users',
            ]:
                await exec(db, f'DELETE FROM {tbl}')

            await seed_users(db)
            product_ids = await seed_products(db)
            line_ids = await seed_production_lines(db)
            eids = await seed_equipment(db)
            ccp_ids = await seed_ccps(db)
            wo_ids = await seed_work_orders(db, product_ids, line_ids)
            lot_ids = await seed_lots(db, wo_ids, product_ids)
            await seed_ccp_records(db, ccp_ids, wo_ids, lot_ids)
            await seed_f_value_records(db, wo_ids, lot_ids, eids)
            await seed_xray_results(db, wo_ids, lot_ids, eids)
            await seed_haccp(db, ccp_ids, wo_ids, lot_ids)
            await seed_iot_sensor_readings(db, eids)
            await seed_notifications(db, lot_ids, wo_ids)

            await db.commit()
            logger.info('=' * 60)
            logger.info('[SEED] ✅ 완료!')
            logger.info(f'  제품: {len(product_ids)}개')
            logger.info(f'  생산지시: {len(wo_ids)}개')
            logger.info(f'  LOT: {len(lot_ids)}개 (Closure Table 구성)')
            logger.info(f'  설비: {len(eids)}대')
            logger.info('  시나리오: DS-20260503-HMR002-0002 (ON_HOLD)')
            logger.info('    └ CCP이탈(살균 117.3°C) + X-Ray NG(금속2.1mm) + F값 미달(7.82)')
            logger.info('=' * 60)
        except Exception as e:
            await db.rollback()
            logger.error(f'[SEED] ❌ 실패: {e}')
            raise


if __name__ == '__main__':
    asyncio.run(run_seeds())
