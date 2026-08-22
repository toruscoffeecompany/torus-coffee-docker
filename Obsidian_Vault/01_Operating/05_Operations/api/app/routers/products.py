from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List
from app.db import get_db
from app.models import Product, ProductImage, InventoryAdjustment
from app.schemas import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductImage as ProductImageSchema,
    ProductImageCreate,
    InventoryAdjustment as InventoryAdjustmentSchema,
    InventoryUpdate,
)

router = APIRouter()


@router.get("/products", response_model=List[ProductSchema])
def list_products(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    featured: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    q = select(Product)
    if status:
        q = q.where(Product.status == status)
    if featured is not None:
        q = q.where(Product.featured == featured)
    if category:
        q = q.where(Product.category == category)
    q = q.offset(skip).limit(limit)
    products = db.execute(q).scalars().all()
    return products


@router.get("/products/{slug}", response_model=ProductSchema)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = db.execute(select(Product).where(Product.slug == slug)).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=ProductSchema, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.patch("/products/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    updates = product.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(db_product, field, value)
    db_product.updated_at = func.datetime("now")
    db.commit()
    db.refresh(db_product)
    return db_product


@router.post("/products/{product_id}/inventory", response_model=InventoryAdjustmentSchema)
def adjust_inventory(product_id: int, adjustment: InventoryUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.track_inventory:
        raise HTTPException(status_code=400, detail="Inventory tracking disabled for product")

    previous = product.quantity_on_hand
    new_quantity = previous + adjustment.delta
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    product.quantity_on_hand = new_quantity
    product.updated_at = func.datetime("now")

    adj = InventoryAdjustment(
        product_id=product_id,
        previous_quantity=previous,
        new_quantity=new_quantity,
        delta=adjustment.delta,
        reason=adjustment.reason,
        note=adjustment.note,
        actor=adjustment.actor,
    )
    db.add(adj)
    db.commit()
    db.refresh(adj)
    return adj


@router.get("/products/{product_id}/images", response_model=List[ProductImageSchema])
def list_product_images(product_id: int, db: Session = Depends(get_db)):
    images = db.execute(
        select(ProductImage).where(ProductImage.product_id == product_id).order_by(ProductImage.sort_order)
    ).scalars().all()
    return images


@router.post("/products/{product_id}/images", response_model=ProductImageSchema, status_code=201)
def add_product_image(product_id: int, image: ProductImageCreate, db: Session = Depends(get_db)):
    db_image = ProductImage(**image.model_dump())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image
