import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

# Import Base and all models so Alembic can detect them
from app.infrastructure.database import Base  # noqa: F401
from app.domains.lot.models import Lot, LotLineage  # noqa: F401
from app.domains.quality.models import Ccp, CcpRecord, FValueRecord, FValueTemperatureSeries, XRayResult  # noqa: F401
from app.domains.production.models import WorkOrder, ProductionLine, Process, ProcessRecord  # noqa: F401
from app.domains.equipment.models import Equipment, IotSensorReading  # noqa: F401
from app.domains.haccp.models import HaccpCheckPlan, HaccpCheckRecord  # noqa: F401
from app.domains.auth.models import User  # noqa: F401
from app.domains.product.models import Product, Bom, BomItem  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Build DB URL from settings (reads DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD env vars)
from app.config import settings as _settings  # noqa: E402
config.set_main_option("sqlalchemy.url", _settings.database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
