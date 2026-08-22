#!/usr/bin/env python3
"""
Heartbeat — Torus Coffee Company
Writes local heartbeat state for PINKCADY → SQUIDSTATION dashboard.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
HEARTBEAT_FILE = VAULT / "10_Skills_Library/05_Operations/Crew/.heartbeat_pinkcady.json"

def write_heartbeat() -> dict:
    data = {
        "host": "PINKCADY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "alive",
        "vault": str(VAULT),
    }
    HEARTBEAT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data

if __name__ == "__main__":
    data = write_heartbeat()
    print(json.dumps(data, indent=2))
