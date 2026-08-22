from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime
from app.db import get_db
from app.models import Order, OrderItem, Customer, Product, InventoryAdjustment
from app.schemas import (
    Order as OrderSchema,
    OrderCreate,
    OrderUpdate,
    OrderItem as OrderItemSchema,
)

router = APIRouter()


@router.get("/orders", response_model=List[OrderSchema])
def list_orders(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    q = select(Order)
    if status:
        q = q.where(Order.status == status)
    if customer_id:
        q = q.where(Order.customer_id == customer_id)
    q = q.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    orders = db.execute(q).scalars().all()
    return orders


@router.post("/orders", response_model=OrderSchema, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    if order.customer_id:
        customer = db.get(Customer, order.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

    now = datetime.utcnow()
    base = f"TCC-{now.strftime('%Y%m%d')}"
    existing = db.execute(
        select(Order).where(Order.order_number.like(f"{base}-%"))
    ).scalars().all()
    seq = len(existing) + 1
    order_number = f"{base}-{seq:04d}"

    db_order = Order(
        customer_id=order.customer_id,
        order_number=order_number,
        status=order.status,
        subtotal_cents=order.subtotal_cents,
        tax_cents=order.tax_cents,
        shipping_cents=order.shipping_cents,
        total_cents=order.total_cents,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        shipping_name=order.shipping_name,
        shipping_address_line1=order.shipping_address_line1,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_zip=order.shipping_zip,
        shipping_country=order.shipping_country,
        notes=order.notes,
    )
    db.add(db_order)
    db.flush()

    for item_data in order.items:
        product = db.get(Product, item_data.product_id)
        if not product:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")

        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price_cents=item_data.unit_price_cents,
            subtotal_cents=item_data.subtotal_cents,
        )
        db.add(db_item)

        if product.track_inventory:
            prev_qty = product.quantity_on_hand
            new_qty = prev_qty - item_data.quantity
            if new_qty < 0:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
            product.quantity_on_hand = new_qty
            product.updated_at = func.datetime("now")

            adj = InventoryAdjustment(
                product_id=product.id,
                previous_quantity=prev_qty,
                new_quantity=new_qty,
                delta=-item_data.quantity,
                reason="order",
                note=f"Order {order_number}",
                actor="api",
            )
            db.add(adj)

    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/orders/{order_id}", response_model=OrderSchema)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/orders/{order_id}", response_model=OrderSchema)
def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.get(Order, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    updates = order.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(db_order, field, value)
    db_order.updated_at = func.datetime("now")
    db.commit()
    db.refresh(db_order)
    return db_order
