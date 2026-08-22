import sqlite3
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
DB_PATH = VAULT / "10_Skills_Library" / "05_Operations" / "data" / "torus_local.db"
conn = sqlite3.connect(DB_PATH)
print("tables:", conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
print("inquiries:", conn.execute("SELECT * FROM inquiries").fetchall())
conn.close()
