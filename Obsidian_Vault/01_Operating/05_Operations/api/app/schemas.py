from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# Shared
class Timestamped(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Products
class ProductBase(Timestamped):
    sku: str
    name: str
    slug: str
    category: str = "Freeze-Dried Fruit"
    status: str = "draft"
    price_cents: int
    cost_cents: Optional[int] = None
    quantity_on_hand: int = 0
    low_stock_threshold: int = 5
    track_inventory: bool = True
    main_image_url: Optional[str] = None
    ingredients: Optional[str] = None
    allergens: Optional[str] = None
    storage_instructions: Optional[str] = None
    shelf_life: Optional[str] = None
    net_weight_oz: Optional[float] = None
    shipping_weight_oz: Optional[float] = None
    ships_us_only: bool = True
    requires_shipping: bool = True
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    featured: bool = False
    sort_order: int = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    price_cents: Optional[int] = None
    cost_cents: Optional[int] = None
    quantity_on_hand: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    track_inventory: Optional[bool] = None
    main_image_url: Optional[str] = None
    ingredients: Optional[str] = None
    allergens: Optional[str] = None
    storage_instructions: Optional[str] = None
    shelf_life: Optional[str] = None
    net_weight_oz: Optional[float] = None
    shipping_weight_oz: Optional[float] = None
    ships_us_only: Optional[bool] = None
    requires_shipping: Optional[bool] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    featured: Optional[bool] = None
    sort_order: Optional[int] = None


class Product(ProductBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductImageBase(Timestamped):
    product_id: int
    image_url: str
    alt_text: Optional[str] = None
    image_type: str = "gallery"
    sort_order: int = 0
    is_primary: bool = False


class ProductImageCreate(ProductImageBase):
    pass


class ProductImage(ProductImageBase):
    id: int
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Customers
class CustomerBase(Timestamped):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    marketing_consent: bool = False
    marketing_consent_at: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    marketing_consent: Optional[bool] = None
    marketing_consent_at: Optional[str] = None
    notes: Optional[str] = None


class Customer(CustomerBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Orders
class OrderItemBase(Timestamped):
    product_id: int
    quantity: int
    unit_price_cents: int
    subtotal_cents: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderBase(Timestamped):
    customer_id: Optional[int] = None
    order_number: str
    status: str = "pending"
    subtotal_cents: int
    tax_cents: int = 0
    shipping_cents: int = 0
    total_cents: int
    payment_method: Optional[str] = None
    payment_status: str = "pending"
    shipping_name: Optional[str] = None
    shipping_address_line1: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_zip: Optional[str] = None
    shipping_country: str = "US"
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    notes: Optional[str] = None


class Order(OrderBase):
    id: int
    items: List[OrderItem] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Inventory
class InventoryAdjustmentBase(Timestamped):
    product_id: int
    previous_quantity: Optional[int] = None
    new_quantity: int
    delta: int
    reason: str = "other"
    note: Optional[str] = None
    actor: str = "system"


class InventoryAdjustmentCreate(InventoryAdjustmentBase):
    pass


class InventoryAdjustment(InventoryAdjustmentBase):
    id: int
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InventoryUpdate(BaseModel):
    delta: int
    reason: str = "other"
    note: Optional[str] = None
    actor: str = "system"


# Admin
class HealthResponse(BaseModel):
    status: str
    database: str
    product_count: int
    customer_count: int
    order_count: int


class AdminStats(BaseModel):
    products: int
    customers: int
    orders: int
    low_stock_count: int
    low_stock_products: List[dict]
