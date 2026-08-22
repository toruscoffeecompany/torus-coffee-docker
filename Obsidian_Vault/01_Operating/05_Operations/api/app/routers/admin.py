from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List
from app.db import get_db
from app.models import Product, Customer, Order
from app.schemas import HealthResponse, AdminStats, Order as OrderSchema

router = APIRouter()


def check_admin_key(request: Request):
    expected = request.app.state.admin_api_key
    provided = request.headers.get("X-Admin-Key")
    if not expected or provided != expected:
        raise HTTPException(status_code=403, detail="Invalid or missing admin key")
    return True


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(select(func.count(Product.id)))
        db_status = "ok"
    except Exception:
        db_status = "error"

    product_count = db.execute(select(func.count(Product.id))).scalar()
    customer_count = db.execute(select(func.count(Customer.id))).scalar()
    order_count = db.execute(select(func.count(Order.id))).scalar()

    return HealthResponse(
        status="ok",
        database=db_status,
        product_count=product_count or 0,
        customer_count=customer_count or 0,
        order_count=order_count or 0,
    )


@router.get("/stats", response_model=AdminStats)
def admin_stats(db: Session = Depends(get_db), _=Depends(check_admin_key)):
    product_count = db.execute(select(func.count(Product.id))).scalar() or 0
    customer_count = db.execute(select(func.count(Customer.id))).scalar() or 0
    order_count = db.execute(select(func.count(Order.id))).scalar() or 0

    low_stock = db.execute(
        select(Product).where(
            Product.track_inventory == True,
            Product.quantity_on_hand <= Product.low_stock_threshold,
        )
    ).scalars().all()

    low_stock_products = [
        {
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "quantity_on_hand": p.quantity_on_hand,
            "low_stock_threshold": p.low_stock_threshold,
        }
        for p in low_stock
    ]

    return AdminStats(
        products=product_count,
        customers=customer_count,
        orders=order_count,
        low_stock_count=len(low_stock_products),
        low_stock_products=low_stock_products,
    )


@router.get("/orders/{order_id}", response_model=OrderSchema)
def admin_get_order(order_id: int, db: Session = Depends(get_db), _=Depends(check_admin_key)):
    db_order = db.get(Order, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order
