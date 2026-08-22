import os
import sys
from pathlib import Path

venv_root = Path(__file__).resolve().parent.parent.parent / "venv"
site_packages = venv_root / "Lib" / "site-packages"
sys.path = [p for p in sys.path if "hermes-agent" not in p]
if str(site_packages) not in sys.path:
    sys.path.insert(0, str(site_packages))

os.chdir(Path(__file__).resolve().parent)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

root = client.get("/")
assert root.status_code == 200, root.text
assert root.json()["name"] == "Torus Coffee Company API"

products = client.get("/api/products?limit=10")
assert products.status_code == 200, products.text
data = products.json()
assert isinstance(data, list)
assert len(data) >= 1
assert data[0]["slug"]

print("API_RUNTIME_OK")
print("root=", root.json())
print("products_count=", len(data))
print("first_product_slug=", data[0]["slug"])
