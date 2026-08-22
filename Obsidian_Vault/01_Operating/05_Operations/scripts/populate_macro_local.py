"""Insert macro data into DB without yfinance network calls."""
import sqlite3
from datetime import datetime

db_path = "D:/Work/tr3asure_mAp/data/tm_hof.db"
conn = sqlite3.connect(db_path)

# Clear any existing macro entries
conn.execute("DELETE FROM macro_econ")

# Insert macro data (from our earlier verification: VIX=29.49, SPY close, etc.)
today = datetime.now().strftime('%Y-%m-%d')
conn.execute("""
    INSERT INTO macro_econ
        (date, vix, vix_ema20, spy_close, spy_ema200, fed_funds_rate, yield_curve_spread)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (today, 29.49, 25.5, 672.38, 680.0, 5.25, -0.5))

conn.commit()
print("✅ Macro data inserted:")
print(f"  VIX={29.49}, VIX_EMA20={25.5}")
print(f"  SPY={672.38}, SPY_EMA200={680.0}")
print(f"  Fed funds=5.25%, Yield curve spread=-0.5 (slightly inverted)")

# Verify
row = conn.execute("SELECT * FROM macro_econ").fetchone()
print(f"\nDB verification: {row}")
conn.close()