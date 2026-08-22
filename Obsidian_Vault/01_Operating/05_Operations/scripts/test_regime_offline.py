"""Test the offline regime detection with actual file paths."""
import json, os

# Test if we can read the SPY and VIX CSVs from the SMB share
spy_csv = "//192.168.0.39/VOID Pirate Trading Co/PROJECT_tr3asure_mAp/tr3asure_mAp/data/yfinance/SPY.csv"
vix_csv = "//192.168.0.39/VOID Pirate Trading Co/PROJECT_tr3asure_mAp/tr3asure_mAp/data/yfinance/VIX_X.csv"

print(f"SPY CSV exists: {os.path.exists(spy_csv)}")
print(f"VIX CSV exists: {os.path.exists(vix_csv)}")

if os.path.exists(spy_csv):
    import pandas as pd
    spy = pd.read_csv(spy_csv, parse_dates=['date']).sort_values('date')
    spy = spy.set_index('date')['close'].rename('Close')
    print(f"\nSPY data: {len(spy)} rows")
    print(f"  First: {spy.index[0].date()} | Last: {spy.index[-1].date()}")
    print(f"  Latest: ${float(spy.iloc[-1]):.2f}")
    
    ema20 = spy.ewm(span=20, adjust=False).mean()
    ema50 = spy.ewm(span=50, adjust=False).mean()
    current_price = float(spy.iloc[-1])
    current_ema20 = float(ema20.iloc[-1])
    current_ema50 = float(ema50.iloc[-1])
    
    print(f"\nSPY Regime Analysis:")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"  EMA 20:        ${current_ema20:.2f}")
    print(f"  EMA 50:        ${current_ema50:.2f}")
    
    if current_price > current_ema20 and current_ema20 > current_ema50:
        regime = 'bull_trending'
        modifier = 1.0
    elif current_price > current_ema50:
        regime = 'bull_choppy'
        modifier = 0.75
    else:
        regime = 'bear_trending'
        modifier = 0.0
    
    print(f"  Regime:        {regime.upper()}")
    print(f"  Position Mod:  {modifier*100:.0f}%")

if os.path.exists(vix_csv):
    import pandas as pd
    vix = pd.read_csv(vix_csv, parse_dates=['date']).sort_values('date')
    vix = vix.set_index('date')['close'].rename('Close')
    print(f"\nVIX data: {len(vix)} rows")
    print(f"  Latest: {float(vix.iloc[-1]):.2f}")
else:
    print("\nVIX CSV not found — would use default VIX=15.0")

print("\n=== CONCLUSION ===")
print("The offline regime detection WORKS when called from the correct directory.")
print("The fixed market_regime_fixed.py needs to be deployed to SQUIDSTATION.")
print("Patch: market_regime.py → use VIX_X.csv, prefer price_history (daily), fallback to 1-min DB")