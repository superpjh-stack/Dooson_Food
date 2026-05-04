"""Initial schema — all MES domain tables

Revision ID: 001
Revises:
Create Date: 2026-05-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="OPERATOR"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("full_name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── products ──────────────────────────────────────────────────────────────
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("unit", sa.String(20), nullable=False, server_default="EA"),
        sa.Column("shelf_life_days", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_products_code", "products", ["code"], unique=True)

    # ── boms ──────────────────────────────────────────────────────────────────
    op.create_table(
        "boms",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── bom_items ─────────────────────────────────────────────────────────────
    op.create_table(
        "bom_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("bom_id", sa.Integer(), sa.ForeignKey("boms.id"), nullable=False),
        sa.Column("material_code", sa.String(50), nullable=False),
        sa.Column("material_name", sa.String(200), nullable=False),
        sa.Column("qty_per_unit", sa.Numeric(12, 4), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── production_lines ──────────────────────────────────────────────────────
    op.create_table(
        "production_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("capacity_per_hour", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit", sa.String(20), nullable=False, server_default="EA"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_production_lines_code", "production_lines", ["code"], unique=True)

    # ── equipment ─────────────────────────────────────────────────────────────
    op.create_table(
        "equipment",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("line_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="IDLE"),
        sa.Column("oee", sa.Numeric(5, 2), nullable=True),
        sa.Column("last_maintained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_equipment_code", "equipment", ["code"], unique=True)

    # ── work_orders ───────────────────────────────────────────────────────────
    op.create_table(
        "work_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("production_line_id", sa.Integer(), sa.ForeignKey("production_lines.id"), nullable=True),
        sa.Column("planned_qty", sa.Numeric(12, 2), nullable=False),
        sa.Column("actual_qty", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(20), nullable=False, server_default="EA"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PLANNED"),
        sa.Column("planned_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("planned_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bom_version", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_work_orders_code", "work_orders", ["code"], unique=True)

    # ── processes ─────────────────────────────────────────────────────────────
    op.create_table(
        "processes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("line_id", sa.Integer(), sa.ForeignKey("production_lines.id"), nullable=True),
        sa.Column("standard_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("is_ccp", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_processes_code", "processes", ["code"], unique=True)

    # ── lots ──────────────────────────────────────────────────────────────────
    op.create_table(
        "lots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("qty", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("produced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("storage_location", sa.String(100), nullable=True),
        sa.Column("qr_code", sa.String(200), nullable=True),
        sa.Column("rfid_tag", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_lots_code", "lots", ["code"], unique=True)

    # ── process_records ───────────────────────────────────────────────────────
    op.create_table(
        "process_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_orders.id"), nullable=False),
        sa.Column("process_id", sa.Integer(), sa.ForeignKey("processes.id"), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("operator", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── lot_lineage (Closure Table) ───────────────────────────────────────────
    op.create_table(
        "lot_lineage",
        sa.Column("ancestor_lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id"), primary_key=True),
        sa.Column("descendant_lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id"), primary_key=True),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("relation_type", sa.String(50), nullable=True),
        sa.Column("qty_used", sa.Numeric(12, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── ccps ──────────────────────────────────────────────────────────────────
    op.create_table(
        "ccps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parameter", sa.String(50), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("limit_min", sa.Numeric(10, 4), nullable=True),
        sa.Column("limit_max", sa.Numeric(10, 4), nullable=True),
        sa.Column("monitoring_freq", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ccps_code", "ccps", ["code"], unique=True)

    # ── ccp_records ───────────────────────────────────────────────────────────
    op.create_table(
        "ccp_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ccp_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ccps.id"), nullable=False),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id"), nullable=True),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("measured_value", sa.Numeric(10, 4), nullable=False),
        sa.Column("measured_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_deviation", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("corrective_action", sa.Text(), nullable=True),
        sa.Column("photo_urls", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── f_value_records ───────────────────────────────────────────────────────
    op.create_table(
        "f_value_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sterilizer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("equipment.id", ondelete="SET NULL"), nullable=False),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id"), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("f0_target", sa.Numeric(8, 4), nullable=True),
        sa.Column("f0_calculated", sa.Numeric(8, 4), nullable=True),
        sa.Column("is_passed", sa.Boolean(), nullable=True),
        sa.Column("ai_prediction", sa.Numeric(8, 4), nullable=True),
        sa.Column("ai_confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── iot_sensor_readings ───────────────────────────────────────────────────
    op.create_table(
        "iot_sensor_readings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("equipment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("equipment.id"), nullable=False),
        sa.Column("sensor_type", sa.String(50), nullable=False),
        sa.Column("value", sa.Numeric(12, 4), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quality", sa.String(20), nullable=False, server_default="GOOD"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_iot_sensor_readings_recorded_at", "iot_sensor_readings", ["recorded_at"])

    # ── xray_results ──────────────────────────────────────────────────────────
    op.create_table(
        "xray_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("machine_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("equipment.id", ondelete="SET NULL"), nullable=False),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id"), nullable=True),
        sa.Column("inspected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("result", sa.String(5), nullable=False),
        sa.Column("contaminant_type", sa.String(50), nullable=True),
        sa.Column("contaminant_size", sa.Numeric(6, 2), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("grad_cam_url", sa.String(500), nullable=True),
        sa.Column("ai_classification", sa.String(50), nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── f_value_temperature_series ────────────────────────────────────────────
    op.create_table(
        "f_value_temperature_series",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("f_value_record_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("f_value_records.id"), nullable=False),
        sa.Column("temperature", sa.Numeric(6, 2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_f_value_temperature_series_recorded_at", "f_value_temperature_series", ["recorded_at"])

    # ── haccp_check_plans ─────────────────────────────────────────────────────
    op.create_table(
        "haccp_check_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ccp_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ccps.id"), nullable=False),
        sa.Column("check_frequency", sa.String(20), nullable=False),
        sa.Column("check_method", sa.Text(), nullable=False),
        sa.Column("corrective_action", sa.Text(), nullable=False),
        sa.Column("responsible_person", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── haccp_check_records ───────────────────────────────────────────────────
    op.create_table(
        "haccp_check_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("haccp_check_plans.id"), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id", ondelete="SET NULL"), nullable=True),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("checked_by", sa.String(100), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("result", sa.String(20), nullable=False),
        sa.Column("measured_values", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("corrective_action_taken", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── notifications ─────────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False, server_default="INFO"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id", ondelete="SET NULL"), nullable=True),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── TimescaleDB hypertables (non-fatal if extension unavailable) ──────────
    try:
        op.execute(
            "SELECT create_hypertable('f_value_temperature_series', 'recorded_at', if_not_exists => TRUE)"
        )
        op.execute(
            "SELECT create_hypertable('iot_sensor_readings', 'recorded_at', if_not_exists => TRUE)"
        )
    except Exception:
        pass  # TimescaleDB not available in this environment


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("haccp_check_records")
    op.drop_table("haccp_check_plans")
    op.drop_index("ix_f_value_temperature_series_recorded_at", table_name="f_value_temperature_series")
    op.drop_table("f_value_temperature_series")
    op.drop_table("xray_results")
    op.drop_index("ix_iot_sensor_readings_recorded_at", table_name="iot_sensor_readings")
    op.drop_table("iot_sensor_readings")
    op.drop_table("f_value_records")
    op.drop_table("ccp_records")
    op.drop_index("ix_ccps_code", table_name="ccps")
    op.drop_table("ccps")
    op.drop_table("lot_lineage")
    op.drop_table("process_records")
    op.drop_index("ix_lots_code", table_name="lots")
    op.drop_table("lots")
    op.drop_index("ix_work_orders_code", table_name="work_orders")
    op.drop_table("work_orders")
    op.drop_index("ix_processes_code", table_name="processes")
    op.drop_table("processes")
    op.drop_index("ix_equipment_code", table_name="equipment")
    op.drop_table("equipment")
    op.drop_index("ix_production_lines_code", table_name="production_lines")
    op.drop_table("production_lines")
    op.drop_table("bom_items")
    op.drop_table("boms")
    op.drop_index("ix_products_code", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
