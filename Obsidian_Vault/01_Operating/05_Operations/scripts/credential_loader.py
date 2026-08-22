#!/usr/bin/env python3
"""
Credential loader for Torus Coffee Company.
Reads secrets from approved vault credential files.
"""
import json
import re
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")

def load_trello_credentials():
    """
    Load Trello API credentials from approved vault file.
    Returns dict with api_key, token, and optional secret.
    """
    creds_path = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
    
    if not creds_path.exists():
        raise FileNotFoundError(f"Trello credentials file not found: {creds_path}")
    
    text = creds_path.read_text(encoding="utf-8")
    api_key = None
    token = None
    secret = None
    
    # Extract values from code blocks
    code_blocks = re.findall(r"`([^`]+)`", text)
    for value in code_blocks:
        if value.startswith("d6ee"):
            api_key = value
        elif value.startswith("ATTA"):
            token = value
        elif value.startswith("7a18"):
            secret = value
    
    if not api_key or not token:
        raise ValueError("Could not parse Trello credentials from file")
    
    result = {
        "api_key": api_key,
        "token": token
    }
    if secret:
        result["secret"] = secret
    
    return result
