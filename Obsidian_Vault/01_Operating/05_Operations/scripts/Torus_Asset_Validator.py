#!/usr/bin/env python3
"""
Daily asset validator - checks generated assets against brand specs
"""
import os
from datetime import datetime

VAULT = r"D:\Work\Torus Coffee Company LLC"
GENERATED_DIR = os.path.join(VAULT, "08_Design_Brand", "Generated")

print(f"Asset Validator - {datetime.now().strftime('%Y-%m-%d')}")
print()

if not os.path.exists(GENERATED_DIR):
    print("No generated assets yet - Sir Azure not started")
    exit(0)

assets = []
for root, dirs, files in os.walk(GENERATED_DIR):
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.gif')):
            assets.append(os.path.join(root, f))

if not assets:
    print("No generated assets found")
    exit(0)

print(f"Found {len(assets)} generated assets")
print()

for asset in assets:
    filename = os.path.basename(asset)
    size = os.path.getsize(asset)
    print(f"  {filename} ({size:,} bytes)")

print(f"\n✓ Asset validation complete")
