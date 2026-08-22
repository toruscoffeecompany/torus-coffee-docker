#!/usr/bin/env python3
"""Torus Coffee Company POS API — self-contained for Docker deployment."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import redis
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("torus-pos")

app = FastAPI(title="Torus POS API")

# Try vault mount first, fall back to local directory
VAULT = Path("/vault")
ORDERS_FILE = VAULT / "04_Products" / "orders.json"
INVENTORY_FILE = VAULT / "04_Products" / "inventory_master.json"

# Redis connection
r = redis.Redis(host="torus-redis", port=6379, decode_responses=True)

@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "ok", "service": "torus-pos", "redis": "connected"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "redis": str(e)})

@app.get("/orders")
def get_orders():
    try:
        if ORDERS_FILE.exists():
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"orders": []}
    except Exception as e:
        logger.error(f"Orders read failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/orders")
def create_order(order: dict):
    try:
        orders = []
        if ORDERS_FILE.exists():
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        orders.append(order)
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2)
        logger.info(f"Order created: {order.get('id', 'unknown')}")
        return {"status": "created", "order": order}
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/products")
def get_products():
    try:
        if INVENTORY_FILE.exists():
            with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"products": {}}
    except Exception as e:
        logger.error(f"Products read failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
