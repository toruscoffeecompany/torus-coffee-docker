from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routers import products, customers, orders, admin, contact, inventory

load_dotenv()

app = FastAPI(
    title="Torus Coffee Company API",
    description="Minimal full-stack API for orders, customers, inventory, and admin.",
    version="0.1.0",
)

app.state.admin_api_key = os.getenv("ADMIN_API_KEY", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(contact.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "Torus Coffee Company API",
        "version": "0.1.0",
        "docs": "/docs",
    }


def create_app():
    return app
