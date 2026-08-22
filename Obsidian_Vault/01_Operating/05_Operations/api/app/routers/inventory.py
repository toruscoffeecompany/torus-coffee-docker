from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from app.db import get_db
from app.models import Product

router = APIRouter()


class InventoryItemResponse(BaseModel):
    sku: str
    name: str
    quantity_on_hand: int
    low_stock_threshold: int
    status: str
    warehouse: Optional[str] = None
    lot: Optional[str] = None

    model_config = {"from_attributes": True}


@router.get("/inventory", response_model=List[InventoryItemResponse])
def list_inventory(
    db: Session = Depends(get_db),
    sku: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    q = select(Product)
    if sku:
        q = q.where(Product.sku == sku)
    products = db.execute(q.offset(skip).limit(limit)).scalars().all()
    results = []
    for product in products:
        stock = product.quantity_on_hand or 0
        reorder_at = product.low_stock_threshold or 0
        state = "Reorder" if stock <= reorder_at else "OK"
        if status and status != state:
            continue
        results.append(
            {
                "sku": product.sku,
                "name": product.name,
                "quantity_on_hand": stock,
                "low_stock_threshold": reorder_at,
                "status": state,
                "warehouse": None,
                "lot": None,
            }
        )
    return results
