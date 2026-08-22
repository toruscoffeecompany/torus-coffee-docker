#!/usr/bin/env python3
"""One-time Miss Pink Discord connect confirmation."""
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from discord_automation_helper import send_connect_confirm_once

if __name__ == "__main__":
    send_connect_confirm_once()
    print("connect_confirm_complete")
