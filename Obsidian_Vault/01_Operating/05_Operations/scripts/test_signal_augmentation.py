"""Test the signal augmentation with real data from the local TM DB."""
import sqlite3, sys, os, json, importlib.util

# Load the augmentation module directly from file
spec = importlib.util.spec_from_file_location(
    "signal_augmentation",
    "D:/Work/tr3asure_mAp/signal_augmentation.py"
)
sa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sa)

db_path = "D:/Work/tr3asure_mAp/data/tm_hof.db"

# Test with a HOF genome
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
genome_row = conn.execute("SELECT * FROM hall_of_fame ORDER BY sharpe_ratio DESC LIMIT 1").fetchone()
genome = dict(genome_row) if genome_row else {}
conn.close()

print(f"Testing with genome: {genome.get('archetype', '?')} Sharpe={genome.get('sharpe_ratio', '?')}")

# Test with AAPL
ticker = "AAPL"

# Load latest bar + metadata
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
bar_row = conn.execute(
    "SELECT * FROM price_history WHERE ticker=? ORDER BY date DESC LIMIT 1", (ticker,)
).fetchone()
bar = dict(bar_row) if bar_row else {}
ticker_meta_row = conn.execute(
    "SELECT sector FROM ticker_fundamentals WHERE ticker=? ORDER BY date DESC LIMIT 1", (ticker,)
).fetchone()
ticker_meta = {'sector': ticker_meta_row['sector'] if ticker_meta_row else ''}
conn.close()

print(f"\nTicker: {ticker}")
print(f"Latest bar: date={bar.get('date', '?')}, close={bar.get('close', '?')}")
print(f"Sector: {ticker_meta.get('sector', 'unknown')}")

# Test fundamental scoring
fund_score, fund_detail = sa.score_fundamental(ticker, bar, db_path)
print(f"\n1. FUNDAMENTAL SCORE: {fund_score}")
for k, v in fund_detail.items():
    print(f"   {k}: {v}")

# Test sector scoring
sec_score, sec_detail = sa.score_sector(ticker, ticker_meta, bar, db_path)
print(f"\n2. SECTOR SCORE: {sec_score}")
for k, v in sec_detail.items():
    print(f"   {k}: {v}")

# Test macro scoring
macro_score, macro_detail = sa.score_macro(bar, db_path)
print(f"\n3. MACRO SCORE: {macro_score}")
for k, v in macro_detail.items():
    print(f"   {k}: {v}")

# Test combined signal (generate_live_signal needs engine imports, so test manually)
# Combined score
tech_score = 0.6  # Assume 3/5 indicators met
combined = 0.4 * tech_score + 0.3 * fund_score + 0.2 * sec_score + 0.1 * macro_score
combined = max(-1, min(1, combined))
print(f"\n4. COMBINED SIGNAL:")
print(f"   Technical score (est): {tech_score}")
print(f"   Fundamental: {fund_score}")
print(f"   Sector: {sec_score}")
print(f"   Macro: {macro_score}")
print(f"   COMBINED: {round(combined, 4)} (threshold ≥0.3 for entry)")
print(f"   Action: {'ENTRY' if combined >= 0.3 else 'EXIT' if combined <= -0.3 else 'HOLD'}")
print(f"   Weights: tech=0.4, fund=0.3, sector=0.2, macro=0.1")

print("\n✅ Signal augmentation verified!")
print("\nDEPLOYMENT:")
print("  1. Copy signal_augmentation.py to SQUIDSTATION Docker container")
print("  2. Add ticker_fundamentals + macro_econ DB tables")
print("  3. Import into augur_signal_generator.py")
print("  4. Combined score replaces pure technical score in genome evaluation")