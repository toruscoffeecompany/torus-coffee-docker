#!/usr/bin/env python3
"""
Validate AI-generated asset against brand specs.
"""
import os
import sys
from PIL import Image

def validate_image(path, min_size=(100, 100), max_size=(4000, 4000)):
    """Check if image meets basic specs."""
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return False

    try:
        img = Image.open(path)
        width, height = img.size

        if width < min_size[0] or height < min_size[1]:
            print(f"Image too small: {width}x{height}")
            return False

        if width > max_size[0] or height > max_size[1]:
            print(f"Image too large: {width}x{height}")
            return False

        print(f"Valid image: {width}x{height}")
        return True
    except Exception as e:
        print(f"Error opening image: {e}")
        return False

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path:
        validate_image(path)
    else:
        print("Usage: python validate_asset.py <image_path>")
