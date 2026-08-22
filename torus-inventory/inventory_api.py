#!/usr/bin/env python3
"""Torus Coffee Company Inventory API."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
from pathlib import Path

app = FastAPI(title="Torus Inventory API")

INVENTORY_PATH = Path(__file__).with_name("inventory_master.json")

def load_inventory():
    try:
        data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        return data
    except Exception as e:
        return {"error": str(e), "products": []}

@app.get("/health")
def health():
    return {"status": "ok", "service": "torus-inventory"}

@app.get("/inventory")
def get_inventory():
    return load_inventory()

@app.get("/")
def root():
    return {"service": "torus-inventory", "endpoints": ["/health", "/inventory"], "source": "inventory_master.json"}
