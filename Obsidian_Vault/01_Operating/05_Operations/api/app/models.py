from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, default="Freeze-Dried Fruit")
    status = Column(String, default="draft", index=True)
    price_cents = Column(Integer, nullable=False)
    cost_cents = Column(Integer)
    quantity_on_hand = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=5)
    track_inventory = Column(Boolean, default=True)
    main_image_url = Column(String)
    ingredients = Column(Text)
    allergens = Column(Text)
    storage_instructions = Column(Text)
    shelf_life = Column(String)
    net_weight_oz = Column(Float)
    shipping_weight_oz = Column(Float)
    ships_us_only = Column(Boolean, default=True)
    requires_shipping = Column(Boolean, default=True)
    seo_title = Column(String)
    seo_description = Column(Text)
    featured = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(String, default=func.datetime("now"))
    updated_at = Column(String, default=func.datetime("now"))

    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    inventory_adjustments = relationship("InventoryAdjustment", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String, nullable=False)
    alt_text = Column(String)
    image_type = Column(String, default="gallery")
    sort_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    created_at = Column(String, default=func.datetime("now"))

    product = relationship("Product", back_populates="images")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    marketing_consent = Column(Boolean, default=False)
    marketing_consent_at = Column(String)
    notes = Column(Text)
    created_at = Column(String, default=func.datetime("now"))
    updated_at = Column(String, default=func.datetime("now"))

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_number = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default="pending", index=True)
    subtotal_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, default=0)
    shipping_cents = Column(Integer, default=0)
    total_cents = Column(Integer, nullable=False)
    payment_method = Column(String)
    payment_status = Column(String, default="pending")
    shipping_name = Column(String)
    shipping_address_line1 = Column(String)
    shipping_city = Column(String)
    shipping_state = Column(String)
    shipping_zip = Column(String)
    shipping_country = Column(String, default="US")
    notes = Column(Text)
    created_at = Column(String, default=func.datetime("now"))
    updated_at = Column(String, default=func.datetime("now"))

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    subtotal_cents = Column(Integer, nullable=False)
    created_at = Column(String, default=func.datetime("now"))

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    previous_quantity = Column(Integer)
    new_quantity = Column(Integer, nullable=False)
    delta = Column(Integer, nullable=False)
    reason = Column(String, default="other")
    note = Column(Text)
    actor = Column(String, default="system")
    created_at = Column(String, default=func.datetime("now"))

    product = relationship("Product", back_populates="inventory_adjustments")
