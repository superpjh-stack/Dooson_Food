import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.product.models import Bom, BomItem, Product
from app.domains.product.schemas import (
    BomCreate, BomDetailResponse, BomItemCreate, BomItemResponse,
    BomResponse, ProductCreate, ProductResponse,
)
from app.shared.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, data: ProductCreate) -> ProductResponse:
        product = Product(**data.model_dump())
        self.db.add(product)
        await self.db.flush()
        logger.info(f"[PRODUCT] Created: {product.code} name={product.name}")
        return ProductResponse.model_validate(product)

    async def list_products(self, is_active: bool = True) -> list[ProductResponse]:
        stmt = select(Product).where(Product.is_active == is_active).order_by(Product.code)
        result = await self.db.execute(stmt)
        return [ProductResponse.model_validate(p) for p in result.scalars().all()]

    async def get_product(self, product_id: int) -> ProductResponse:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product is None:
            raise NotFoundException(f"제품을 찾을 수 없습니다: {product_id}")
        return ProductResponse.model_validate(product)

    async def create_bom(self, data: BomCreate) -> BomResponse:
        bom = Bom(**data.model_dump())
        self.db.add(bom)
        await self.db.flush()
        logger.info(f"[PRODUCT] BOM created: product_id={bom.product_id} version={bom.version}")
        response = BomResponse.model_validate(bom)
        response.items_count = 0
        return response

    async def get_bom_detail(self, bom_id: int) -> BomDetailResponse:
        bom_result = await self.db.execute(select(Bom).where(Bom.id == bom_id))
        bom = bom_result.scalar_one_or_none()
        if bom is None:
            raise NotFoundException(f"BOM을 찾을 수 없습니다: {bom_id}")
        items_result = await self.db.execute(
            select(BomItem).where(BomItem.bom_id == bom_id).order_by(BomItem.id)
        )
        items = [BomItemResponse.model_validate(i) for i in items_result.scalars().all()]
        detail = BomDetailResponse.model_validate(bom)
        detail.items = items
        detail.items_count = len(items)
        return detail

    async def get_active_bom(self, product_id: int) -> BomResponse | None:
        result = await self.db.execute(
            select(Bom)
            .where(Bom.product_id == product_id, Bom.is_active.is_(True))
            .order_by(Bom.effective_from.desc())
            .limit(1)
        )
        bom = result.scalar_one_or_none()
        if bom is None:
            return None
        items_count_result = await self.db.execute(
            select(BomItem).where(BomItem.bom_id == bom.id)
        )
        items_count = len(items_count_result.scalars().all())
        response = BomResponse.model_validate(bom)
        response.items_count = items_count
        return response

    async def add_bom_item(self, data: BomItemCreate) -> BomItemResponse:
        bom_result = await self.db.execute(select(Bom).where(Bom.id == data.bom_id))
        if bom_result.scalar_one_or_none() is None:
            raise NotFoundException(f"BOM을 찾을 수 없습니다: {data.bom_id}")
        item = BomItem(**data.model_dump())
        self.db.add(item)
        await self.db.flush()
        logger.info(
            f"[PRODUCT] BomItem added: bom_id={item.bom_id} material={item.material_code} "
            f"qty={item.qty_per_unit}{item.unit}"
        )
        return BomItemResponse.model_validate(item)
