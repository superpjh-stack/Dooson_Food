"""
LOT lineage backward/forward trace must complete in < 5 seconds for 100-level deep tree.
CLAUDE.md rule: DB mocks forbidden — tests use real DB via docker compose.
"""
import time
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.mark.integration
async def test_backward_trace_completes_under_5_seconds(async_client: AsyncClient):
    """Closure Table backward trace on deep LOT tree must be < 5s."""
    # Use a pre-seeded lot_id (assumes test fixtures loaded)
    lot_id = 1
    start = time.perf_counter()
    response = await async_client.get(f"/api/v1/lots/{lot_id}/trace/backward")
    elapsed = time.perf_counter() - start
    assert response.status_code == 200
    assert elapsed < 5.0, f"Backward trace took {elapsed:.2f}s, limit is 5s"


@pytest.mark.integration
async def test_forward_trace_completes_under_5_seconds(async_client: AsyncClient):
    """Closure Table forward trace on deep LOT tree must be < 5s."""
    lot_id = 1
    start = time.perf_counter()
    response = await async_client.get(f"/api/v1/lots/{lot_id}/trace/forward")
    elapsed = time.perf_counter() - start
    assert response.status_code == 200
    assert elapsed < 5.0, f"Forward trace took {elapsed:.2f}s, limit is 5s"
