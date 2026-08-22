#!/usr/bin/env python3
"""
Organize generated assets into correct vault folders.
"""
import os
import shutil
import sys
from datetime import datetime

VAULT = r"D:\Work\Torus Coffee Company LLC"

def organize_asset(source_path, asset_type):
    """Move asset to correct folder based on type."""
    if asset_type == "product":
        dest = os.path.join(VAULT, "04_Products", "Product_Photos")
    elif asset_type == "social":
        dest = os.path.join(VAULT, "06_Growth_Marketing", "Social_Media")
    elif asset_type == "vendor":
        dest = os.path.join(VAULT, "08_Design_Brand", "Vendor_Booth")
    elif asset_type == "email":
        dest = os.path.join(VAULT, "08_Design_Brand", "Email_Signatures")
    else:
        dest = os.path.join(VAULT, "08_Design_Brand", "Generated")

    os.makedirs(dest, exist_ok=True)
    filename = os.path.basename(source_path)
    dest_path = os.path.join(dest, filename)

    # Add timestamp if file exists
    if os.path.exists(dest_path):
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = os.path.join(dest, f"{name}_{timestamp}{ext}")

    shutil.move(source_path, dest_path)
    print(f"Moved {source_path} -> {dest_path}")
    return dest_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python organize_assets.py <source_path> <asset_type>")
        print("Types: product, social, vendor, email, generated")
        sys.exit(1)

    organize_asset(sys.argv[1], sys.argv[2])
