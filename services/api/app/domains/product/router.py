import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.product.schemas import (
    BomCreate, BomDetailResponse, BomItemCreate, BomItemResponse,
    BomResponse, ProductCreate, ProductResponse,
)
from app.domains.product.service import ProductService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["제품/BOM 관리"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


@router.get('/products', response_model=list[ProductResponse])
async def list_products(
    is_active: bool = Query(True),
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"[API] GET /products is_active={is_active}")
    return await service.list_products(is_active=is_active)


@router.post('/products', response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"[API] POST /products code={payload.code}")
    return await service.create_product(payload)


@router.get('/products/{product_id}', response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"[API] GET /products/{product_id}")
    return await service.get_product(product_id)


@router.get('/products/{product_id}/bom', response_model=BomResponse | None)
async def get_active_bom(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"[API] GET /products/{product_id}/bom")
    return await service.get_active_bom(product_id)


@router.post('/boms', response_model=BomResponse, status_code=201)
async def create_bom(
    payload: BomCreate,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"[API] POST /boms product_id={payload.product_id} version={payload.version}")
    return await service.create_bom(payload)


@router.get('/boms/{bom_id}', response_model=BomDetailResponse)
async def get_bom_detail(
    bom_id: int,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"[API] GET /boms/{bom_id}")
    return await service.get_bom_detail(bom_id)


@router.post('/boms/{bom_id}/items', response_model=BomItemResponse, status_code=201)
async def add_bom_item(
    bom_id: int,
    payload: BomItemCreate,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"[API] POST /boms/{bom_id}/items material={payload.material_code}")
    payload_with_id = payload.model_copy(update={'bom_id': bom_id})
    return await service.add_bom_item(payload_with_id)
