#!/usr/bin/env python3
"""Run done_card_verifier.py via venv."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\done_card_verifier.py")
VENV_PY = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\python.exe")

result = subprocess.run([str(VENV_PY), str(SCRIPT)], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
