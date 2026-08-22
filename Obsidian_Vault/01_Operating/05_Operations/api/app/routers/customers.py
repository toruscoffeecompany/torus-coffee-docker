from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from typing import Optional, List
from app.db import get_db
from app.models import Customer, Order
from app.schemas import (
    Customer as CustomerSchema,
    CustomerCreate,
    CustomerUpdate,
)

router = APIRouter()


@router.get("/customers", response_model=List[CustomerSchema])
def list_customers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    customers = db.execute(select(Customer).offset(skip).limit(limit)).scalars().all()
    return customers


@router.get("/customers/search", response_model=List[CustomerSchema])
def search_customers(
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
):
    like = f"%{q}%"
    qry = select(Customer).where(
        or_(
            Customer.email.ilike(like),
            Customer.first_name.ilike(like),
            Customer.last_name.ilike(like),
        )
    )
    return db.execute(qry.limit(limit)).scalars().all()


@router.post("/customers", response_model=CustomerSchema, status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(Customer).where(Customer.email == customer.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/customers/{customer_id}", response_model=CustomerSchema)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.patch("/customers/{customer_id}", response_model=CustomerSchema)
def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = db.get(Customer, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    updates = customer.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(db_customer, field, value)
    db_customer.updated_at = func.datetime("now")
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/customers/{customer_id}/summary")
def customer_summary(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    orders = db.execute(select(Order).where(Order.customer_id == customer_id)).scalars().all()
    total_orders = len(orders)
    total_spent_cents = sum(order.total_cents or 0 for order in orders)
    last_order_at = max((order.created_at for order in orders if order.created_at), default=None)
    return {
        "id": customer.id,
        "email": customer.email,
        "name": f"{customer.first_name or ''} {customer.last_name or ''}".strip() or customer.email,
        "total_orders": total_orders,
        "total_spent_cents": total_spent_cents,
        "last_order_at": last_order_at,
    }
